from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, create_model

from avrodantic.core.entities.avro_schema import AvroSchema
from avrodantic.exceptions import SchemaValidationError


class PydanticModelGenerator:
    def __init__(self):
        self._generated_models: Dict[str, Type] = {}

    def generate(self, schema: AvroSchema) -> Type[BaseModel]:
        """Generate a Pydantic model from an Avro schema."""
        return self._parse_type(schema.schema_json)

    def _parse_type(self, avro_type: Any) -> Type:
        if isinstance(avro_type, dict):
            return self._handle_complex_type(avro_type)
        elif isinstance(avro_type, list):
            return self._handle_union(avro_type)
        else:
            return self._map_primitive_type(avro_type)

    def _handle_complex_type(self, schema: dict) -> Type:
        avro_type = schema["type"]

        if avro_type == "record":
            return self._generate_record_model(schema)
        elif avro_type == "enum":
            return self._generate_enum_model(schema)
        elif avro_type == "array":
            return List[self._parse_type(schema["items"])]  # noqa: F821
        elif avro_type == "map":
            return Dict[str, self._parse_type(schema["values"])]  # noqa: F821
        elif avro_type == "fixed":
            return bytes  # Or use constrained types for fixed-length validation
        else:
            raise SchemaValidationError(f"Unsupported complex type: {avro_type}")

    def _generate_record_model(self, schema: dict) -> Type[BaseModel]:
        name = self._get_qualified_name(schema)

        if name in self._generated_models:
            return self._generated_models[name]

        fields = {}
        for field in schema.get("fields", []):
            field_name = field["name"]
            field_type = self._parse_type(field["type"])
            default = field.get("default")

            if default is not None:
                fields[field_name] = (field_type, Field(default=default))
            else:
                fields[field_name] = (field_type, ...)

        model = create_model(name, **fields)
        self._generated_models[name] = model
        return model

    def _generate_enum_model(self, schema: dict) -> Enum:
        name = self._get_qualified_name(schema)
        symbols = schema["symbols"]

        if name in self._generated_models:
            return self._generated_models[name]

        enum_cls = Enum(name, {s: s for s in symbols})
        self._generated_models[name] = enum_cls
        return enum_cls

    def _handle_union(self, types: list) -> Type:
        null_index = next((i for i, t in enumerate(types) if t == "null"), None)
        non_null_types = [t for t in types if t != "null"]

        if null_index is not None:
            if len(non_null_types) == 0:
                return type(None)
            elif len(non_null_types) == 1:
                return Optional[self._parse_type(non_null_types[0])]
            else:
                return Optional[
                    Union[tuple(self._parse_type(t) for t in non_null_types)]
                ]
        else:
            return Union[tuple(self._parse_type(t) for t in types)]

    def _map_primitive_type(self, avro_type: str) -> Type:
        type_map = {
            "null": type(None),
            "boolean": bool,
            "int": int,
            "long": int,
            "float": float,
            "double": float,
            "bytes": bytes,
            "string": str,
        }
        try:
            return type_map[avro_type]
        except KeyError:
            raise SchemaValidationError(f"Unsupported primitive type: {avro_type}")

    def _get_qualified_name(self, schema: dict) -> str:
        namespace = schema.get("namespace", "")
        name = schema["name"]
        return f"{namespace}_{name}" if namespace else name
