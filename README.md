# AvroDantic

In many modern IoT projects, JSON is often overused, causing downstream consumers to face challenges with schema evolution. Regardeless Python's dynamic nature, handling these challenges requires complex logic. This project aims to streamline the management of data evolution by leveraging Avro as an intermediate layer. By adopting Avro, we enhance forward and backward compatibility, simplifying the data management process and reducing complexity for downstream systems.
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
