import os 
import json
from avrodantic.core.entities.avro_schema import AvroSchema

class LocalSchemaRegistry:
    def __init__(self, schema_dir: str = ".registry"):
        self.schema_dir = schema_dir
        os.makedirs(self.schema_dir, exist_ok=True)
    
    def register(self, schema: AvroSchema) -> int:
        schema_file = os.path.join(self.schema_dir, f"{schema.schema_id}_{schema.schema_version}.json")
        with open(schema_file, "w") as f:
            json.dump(schema.schema_json, f)
        return schema.schema_version
        

    def get_schema(self, schema_id: str, schema_version: int) -> AvroSchema:
        schema_file = os.path.join(self.schema_dir, f"{schema_id}_{schema_version}.json")
        with open(schema_file, "r") as f:
            schema_json = json.load(f)
        return AvroSchema(schema_id, schema_json, schema_version)
        