from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from elasticsearch import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch
from datetime import datetime

app = FastAPI()

# ✅ Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing, restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ✅ Initialize Elasticsearch
es = Elasticsearch("http://localhost:9200")

# ✅ Load AI model once to optimize performance
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# ✅ Function to generate AI embeddings
def get_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

# ✅ Pydantic model with validation
class LogEntry(BaseModel):
    log_text: str = Field(..., min_length=1, description="Log text cannot be empty")
    resolution: str = Field(..., min_length=1, description="Resolution cannot be empty")

    def validate(self):
        if self.log_text.strip() == self.resolution.strip():
            raise ValueError("log_text and resolution must be different.")

@app.post("/logs/")
async def add_log(log: LogEntry):
    # ✅ Ensure log_text and resolution are not the same
    if log.log_text.strip() == log.resolution.strip():
        raise HTTPException(status_code=400, detail="log_text and resolution must be different.")

    search_query = {
        "query": {
            "match_phrase": {  # Use match_phrase for exact match
                "log_text": log.log_text
            }
        }
    }

    response = es.search(index="logs_index", body=search_query)

    if response["hits"]["total"]["value"] > 0:
        # ✅ Log already exists, update count safely
        log_id = response["hits"]["hits"][0]["_id"]
        es.update(index="logs_index", id=log_id, body={
            "script": {
                "source": """
                    if (ctx._source.containsKey('count')) {
                        ctx._source.count += 1;
                    } else {
                        ctx._source.count = 1;
                    }
                """,
                "lang": "painless"
            }
        }, refresh="wait_for")  # Ensure consistency

        return {"message": "Log already exists, count updated!"}
    else:
        # ✅ Insert new log
        log_entry = {
            "log_text": log.log_text,
            "log_embedding": get_embedding(log.log_text),
            "resolution": log.resolution,
            "timestamp": datetime.utcnow().isoformat(),  # Use correct timestamp format
            "count": 1
        }
        es.index(index="logs_index", body=log_entry, refresh="wait_for")
        return {"message": "New log inserted successfully!"}

@app.get("/logs/")
async def get_logs():
    query = {"query": {"match_all": {}}}
    response = es.search(index="logs_index", body=query, size=10)
    return response["hits"]["hits"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
