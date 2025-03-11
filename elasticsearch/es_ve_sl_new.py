from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch

es = Elasticsearch("http://localhost:9200")

# AI-based embedding function
def get_embedding(text):
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

log_text = "Service crashed due to memory overload"

# 1️⃣ 🔍 **Check if the log already exists**
search_query = {
    "query": {
        "match": {
            "log_text": log_text
        }
    }
}

response = es.search(index="logs_index", body=search_query)

if response["hits"]["total"]["value"] > 0:
    # 2️⃣ ✅ **Log already exists → Update count**
    log_id = response["hits"]["hits"][0]["_id"]  # Get existing document ID
    es.update(index="logs_index", id=log_id, body={
        "script": {
            "source": "ctx._source.count += 1",
            "lang": "painless"
        }
    })
    print("Log already exists, count updated!")
else:
    # 3️⃣ ❌ **Log does not exist → Insert new log**
    log_entry = {
        "log_text": log_text,
        "log_embedding": get_embedding(log_text),
        "resolution": "Increase memory allocation",
        "timestamp": "2025-02-19T10:00:00",
        "count": 1
    }

    es.index(index="logs_index", body=log_entry)
    print("New log inserted successfully!")
