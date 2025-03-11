from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch

es = Elasticsearch("http://localhost:9200")

def get_embedding(text):
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

log_entry = {
    "log_text": "Service crashed due to memory overload",
    "log_embedding": get_embedding("Service crashed due to memory overload"),
    "resolution": "Increase memory allocation",
    "timestamp": "2025-02-19T10:00:00"
}

# Use a unique identifier for deduplication (e.g., a hash of the log_text)
log_id = hash(log_entry["log_text"])

es.update(index="logs_index", id=log_id, body={
    "script": {
        "source": "ctx._source.count += 1",
        "lang": "painless"
    },
    "upsert": {
        "log_entry": log_entry,
        "count": 1
    }
})
#es.index(index="logs_index", id=log_id, body=log_entry)

#es.index(index="logs_index", body=log_entry)
print("Log stored successfully!")
