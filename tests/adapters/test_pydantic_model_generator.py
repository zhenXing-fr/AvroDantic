import pytest

from avrodantic.adapters.pydantic_generator.pydantic_model_generator import (
    PydanticModelGenerator,
)
from avrodantic.core.entities.avro_schema import AvroSchema


@pytest.fixture
def generator():
    return PydanticModelGenerator()


def test_primitive_types(generator):
    schema = AvroSchema(
        schema_id="test-v1",
        schema_version=1,
        schema_json={
            "type": "record",
            "name": "TestRecord",
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "age", "type": "int"},
            ],
        },
    )

    model = generator.generate(schema)
    instance = model(name="Alice", age=30)
    assert instance.name == "Alice"
    assert instance.age == 30


def test_nested_record(generator):
    schema = AvroSchema(
        schema_id="user-v1",
        schema_version=1,
        schema_json={
            "type": "record",
            "name": "User",
            "fields": [
                {"name": "name", "type": "string"},
                {
                    "name": "address",
                    "type": {
                        "type": "record",
                        "name": "Address",
                        "fields": [
                            {"name": "street", "type": "string"},
                            {"name": "city", "type": "string"},
                        ],
                    },
                },
            ],
        },
    )

    model = generator.generate(schema)
    print(model)
    address = {"street": "123 Main St", "city": "Springfield"}
    user = model(name="Bob", address=address)
    assert user.address.street == "123 Main St"


def test_union_type(generator):
    schema = AvroSchema(
        schema_id="doc-v1",
        schema_version=1,
        schema_json={
            "type": "record",
            "name": "Document",
            "fields": [
                {"name": "content", "type": ["null", "string"], "default": None}
            ],
        },
    )

    model = generator.generate(schema)
    print(model)
    doc1 = model(content=None)
    assert doc1.content is None

    doc2 = model(content="Hello")
    assert doc2.content == "Hello"


def test_enum(generator):
    schema = AvroSchema(
        schema_id="status-v1",
        schema_version=1,
        schema_json={
            "type": "enum",
            "name": "Status",
            "symbols": ["PENDING", "ACTIVE", "INACTIVE"],
        },
    )

    model = generator.generate(schema)
    assert model("PENDING").value == "PENDING"
    with pytest.raises(ValueError, match="'INVALID' is not a valid Status"):
        model("INVALID")
