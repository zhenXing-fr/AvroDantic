from pydantic import ValidationError

from avrodantic.adapters.pydantic_generator.pydantic_model_generator import (
    PydanticModelGenerator,
)
from avrodantic.adapters.schema_resigtry.local_registry import LocalSchemaRegistry
from avrodantic.adapters.serializers.avro_serializer import AvroSerializer
from avrodantic.exceptions import (
    SchemaNotFoundError,
    SchemaValidationError,
    SerializationError,
)


class ValidateAndSerializeUseCase:
    def __init__(
        self,
        registry: LocalSchemaRegistry,
        serializer: AvroSerializer,
        model_generator: PydanticModelGenerator,
    ):
        self.registry = registry
        self.serializer = serializer
        self.model_generator = model_generator

    def execute(self, json_data: dict, schema_id: str, schema_version: int) -> bytes:
        """Validate and serialize JSON data for a given schema version."""
        try:
            schema = self.registry.get_schema(schema_id, schema_version)
            model_cls = self.model_generator.generate(schema)
            validated_data = model_cls(**json_data).model_dump()
            return self.serializer.serialize(validated_data, schema)

        except SchemaNotFoundError as e:
            raise SchemaValidationError(
                f"Schema {schema_id} v{schema_version} not found"
            ) from e
        except ValidationError as e:
            raise SchemaValidationError(f"Validation failed: {str(e)}") from e
        except SerializationError as e:
            raise SerializationError(f"Serialization failed: {str(e)}") from e
