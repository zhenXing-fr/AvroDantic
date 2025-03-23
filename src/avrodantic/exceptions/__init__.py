"""Exceptions for AvroDantic."""


class SchemaValidationError(Exception):
    """Raised when data validation against a schema fails."""


class SerializationError(Exception):
    """Raised when serialization to Avro fails."""


class SchemaNotFoundError(Exception):
    """Raised when a schema is not found in the registry."""
