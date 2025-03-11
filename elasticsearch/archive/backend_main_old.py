from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch

app = FastAPI()
es = Elasticsearch("http://localhost:9200")

# Load AI model once to optimize performance
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Function to generate AI embeddings
def get_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

# Pydantic model for request data
class LogEntry(BaseModel):
    log_text: str
    resolution: str

@app.post("/logs/")
async def add_log(log: LogEntry):
    # Check if log exists in Elasticsearch
    search_query = {
        "query": {
            "match": {
                "log_text": log.log_text
            }
        }
    }

    response = es.search(index="logs_index", body=search_query)

    if response["hits"]["total"]["value"] > 0:
        # Log already exists, update count
        log_id = response["hits"]["hits"][0]["_id"]
        es.update(index="logs_index", id=log_id, body={
            "script": {
                "source": "ctx._source.count += 1",
                "lang": "painless"
            }
        })
        return {"message": "Log already exists, count updated!"}
    else:
        # Insert new log
        log_entry = {
            "log_text": log.log_text,
            "log_embedding": get_embedding(log.log_text),
            "resolution": log.resolution,
            "timestamp": "2025-02-19T10:00:00",
            "count": 1
        }
        es.index(index="logs_index", body=log_entry)
        return {"message": "New log inserted successfully!"}

@app.get("/logs/")
async def get_logs():
    query = {"query": {"match_all": {}}}
    response = es.search(index="logs_index", body=query, size=10)
    return response["hits"]["hits"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
