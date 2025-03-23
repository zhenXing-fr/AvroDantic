# AvroDantic

In many modern IoT projects, JSON is often overused, causing downstream consumers to face challenges with schema evolution. Regardeless Python's dynamic nature, handling these challenges requires complex logic. This project aims to streamline the management of data evolution by leveraging Avro as an intermediate layer. By adopting Avro, we enhance forward and backward compatibility, simplifying the data management process and reducing complexity for downstream systems.

```mermaid
sequenceDiagram
    participant User
    participant UseCase as ValidateAndSerializeUseCase
    participant Registry as LocalSchemaRegistry
    participant Generator as PydanticModelGenerator
    participant Serializer as AvroSerializer
    
    User->>UseCase: execute(json_data, schema_id, version)
    activate UseCase
    
    UseCase->>Registry: get_schema(schema_id, version)
    activate Registry
    Registry-->>UseCase: AvroSchema
    deactivate Registry
    
    UseCase->>Generator: generate(schema)
    activate Generator
    Generator-->>UseCase: PydanticModel
    deactivate Generator
    
    UseCase->>UseCase: Validate data using PydanticModel
    alt Validation Success
        UseCase->>Serializer: serialize(validated_data, schema)
        activate Serializer
        Serializer-->>UseCase: avro_bytes
        deactivate Serializer
        
        UseCase-->>User: Return avro_bytes
    else Validation Failure
        UseCase-->>User: Raise SchemaValidationError
    end
    
    deactivate UseCase
    
    alt Error Cases
        Registry--x UseCase: SchemaNotFoundError
        UseCase--x User: Propagate error
        
        Serializer--x UseCase: SerializationError
        UseCase--x User: Propagate error
    end
---
For downstream users :
---
```mermaid
sequenceDiagram
    participant Spark as PySpark
    participant Kafka
    
    User->>Spark: read_avro(data_path)
    Spark->>Registry: get_schema(schema_id)
    Registry-->>Spark: AvroSchema
    Spark->>Serializer: deserialize(avro_bytes, schema)
    Serializer-->>Spark: Python dict
    
    User->>Kafka: produce(topic, avro_bytes)
    Kafka->>Registry: get_schema(schema_id)
    Registry-->>Kafka: AvroSchema
    Kafka->>Serializer: deserialize(avro_bytes, schema)
