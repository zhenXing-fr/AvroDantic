class AvroSchema:
    def __init__(self, schema_id: str, schema_json: dict, schema_version: int):
        self.schema_version = schema_version
        self.schema_id = schema_id
        self.schema_json = schema_json

    def __eq__(self, other):
        if not isinstance(other, AvroSchema):
            return False
        return (
            self.schema_id == other.schema_id
            and self.schema_json == other.schema_json
            and self.schema_version == other.schema_version
        )
