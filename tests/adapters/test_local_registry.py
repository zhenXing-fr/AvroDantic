from avrodantic.adapters.schema_resigtry.local_registry import LocalSchemaRegistry
from avrodantic.core.entities.avro_schema import AvroSchema


def test_register_and_get_schema():
    schema = AvroSchema("test", {"type": "record", "name": "test", "fields": []}, 1)
    registry = LocalSchemaRegistry()
    registry.register(schema)
    assert registry.get_schema("test", 1) == schema
