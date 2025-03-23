from io import BytesIO

import fastavro

from avrodantic.core.entities.avro_schema import AvroSchema
from avrodantic.exceptions import SerializationError


class AvroSerializer:
    def serialize(self, data: dict, schema: AvroSchema) -> bytes:
        """Serialize validated data to Avro binary format."""
        try:
            parsed_schema = fastavro.parse_schema(schema.schema_json)

            with BytesIO() as buf:
                fastavro.schemaless_writer(buf, parsed_schema, data)
                avro_bytes = buf.getvalue()

            return avro_bytes
        except Exception as e:
            raise SerializationError(f"Avro serialization failed: {str(e)}") from e
