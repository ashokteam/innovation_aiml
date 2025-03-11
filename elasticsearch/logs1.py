from elasticsearch import Elasticsearch
import sys
sys.path.append("c:/Users/eashvee/OneDrive - Ericsson/Ashok/EO/Innovation/ai-chatbot/elasticsearch/")
from es_ve_sl import get_embedding, es

es = Elasticsearch("http://localhost:9200")
log_data = {
    "log_text": "Error: Connection timeout",
    "log_embedding": get_embedding("Error: Connection timeout"),
    "resolution": "Increase timeout settings in config.yaml",
    "timestamp": "2025-02-19T10:00:00"
}


es.index(index="logs_index", document=log_data)
