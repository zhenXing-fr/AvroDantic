from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from avrodantic.core.entities.avro_schema import AvroSchema
from avrodantic.core.use_cases.validate_and_serialiez import ValidateAndSerializeUseCase
from avrodantic.exceptions import (
    SchemaNotFoundError,
    SchemaValidationError,
    SerializationError,
)


@pytest.fixture
def mock_dependencies():
    return {"registry": Mock(), "serializer": Mock(), "model_generator": Mock()}


@pytest.fixture
def temperature_schema():
    return AvroSchema(
        schema_id="temperature",
        schema_json={
            "type": "record",
            "name": "Temperature",
            "fields": [
                {"name": "value", "type": "float"},
                {"name": "unit", "type": "string", "default": "Celsius"},
            ],
        },
        schema_version=1,
    )


def test_happy_path(mock_dependencies, temperature_schema):
    mock_dependencies["registry"].get_schema.return_value = temperature_schema

    class TempModel(BaseModel):
        value: float
        unit: str = "Celsius"

    mock_dependencies["model_generator"].generate.return_value = TempModel
    mock_dependencies["serializer"].serialize.return_value = b"serialized_data"

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)
    result = use_case.execute({"value": 25.3}, "temperature", 1)

    assert result == b"serialized_data"
    mock_dependencies["registry"].get_schema.assert_called_with("temperature", 1)
    mock_dependencies["serializer"].serialize.assert_called_with(
        {"value": 25.3, "unit": "Celsius"}, temperature_schema
    )


def test_invalid_data(mock_dependencies, temperature_schema):
    mock_dependencies["registry"].get_schema.return_value = temperature_schema

    class TempModel(BaseModel):
        value: float
        unit: str = "Celsius"

    mock_dependencies["model_generator"].generate.return_value = TempModel

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)

    with pytest.raises(SchemaValidationError):
        use_case.execute({"value": "invalid"}, "temperature", 1)


def test_missing_schema(mock_dependencies):
    mock_dependencies["registry"].get_schema.side_effect = SchemaNotFoundError

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)

    with pytest.raises(SchemaValidationError):
        use_case.execute({"value": 25.3}, "temperature", 1)


def test_serialization_failure(mock_dependencies, temperature_schema):
    mock_dependencies["registry"].get_schema.return_value = temperature_schema
    mock_dependencies["serializer"].serialize.side_effect = SerializationError(
        "Test error"
    )

    class TempModel(BaseModel):
        value: float
        unit: str = "Celsius"

    mock_dependencies["model_generator"].generate.return_value = TempModel

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)

    with pytest.raises(SerializationError):
        use_case.execute({"value": 25.3}, "temperature", 1)


def test_schema_evolution(mock_dependencies):
    # Test forward compatibility
    schema_v2 = AvroSchema(
        schema_id="sensor",
        schema_version=2,
        schema_json={
            "type": "record",
            "name": "Sensor",
            "fields": [
                {"name": "temp", "type": "float"},
                {"name": "unit", "type": "string", "default": "Celsius"},
            ],
        },
    )

    mock_dependencies["registry"].get_schema.return_value = schema_v2

    serialized_data = {}

    def capture_serialize(data, schema):
        serialized_data.update(data)
        return b"dummy"

    mock_dependencies["serializer"].serialize.side_effect = capture_serialize

    class SensorModelV2(BaseModel):
        temp: float
        unit: str = "Celsius"

    mock_dependencies["model_generator"].generate.return_value = SensorModelV2

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)

    result = use_case.execute({"temp": 25.3}, "sensor", 2)

    assert serialized_data.get("unit") == "Celsius", "Default value not applied"
    assert serialized_data["temp"] == 25.3, "Original value incorrect"
    assert result == b"dummy", "Should return serialized bytes"


def test_complex_types(mock_dependencies):
    schema = AvroSchema(
        schema_id="complex",
        schema_version=1,
        schema_json={
            "type": "record",
            "name": "ComplexData",
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "metadata", "type": {"type": "map", "values": "string"}},
                {"name": "readings", "type": {"type": "array", "items": "float"}},
            ],
        },
    )

    class ComplexModel(BaseModel):
        id: str
        metadata: dict[str, str]
        readings: list[float]

    mock_dependencies["registry"].get_schema.return_value = schema
    mock_dependencies["model_generator"].generate.return_value = ComplexModel

    use_case = ValidateAndSerializeUseCase(**mock_dependencies)

    valid_data = {
        "id": "sensor-1",
        "metadata": {"location": "room-101"},
        "readings": [25.3, 26.0],
    }
    expected_bytes = b"complex_data"
    mock_dependencies["serializer"].serialize.return_value = expected_bytes

    result = use_case.execute(valid_data, "complex", 1)
    assert result == expected_bytes, "Should return exact complex data bytes"
    mock_dependencies["serializer"].serialize.assert_called_once_with(
        {
            "id": "sensor-1",
            "metadata": {"location": "room-101"},
            "readings": [25.3, 26.0],
        },
        schema,
    )
