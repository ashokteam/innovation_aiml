from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

index_mapping = {
    "mappings": {
        "properties": {
            "log_text": { "type": "text" },
            "log_embedding": { "type": "dense_vector", "dims": 384 }, 
            "resolution": { "type": "text" },
            "timestamp": { "type": "date" },
            "count":{ "type": "integer" }
        }
    }
}

es.indices.create(index="logs_index", body=index_mapping, ignore=400)
print("Index created successfully!")
