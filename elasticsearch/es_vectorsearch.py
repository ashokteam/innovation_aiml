import sys
sys.path.append("c:/Users/eashvee/OneDrive - Ericsson/Ashok/EO/Innovation/ai-chatbot/elasticsearch/")
from es_ve_sl import get_embedding, es
query_embedding = get_embedding("Error Connection timeout")

search_query = {
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'log_embedding') + 1.0",
                "params": {"query_vector": query_embedding}
            }
        }
    }
}

results = es.search(index="logs_index", body=search_query)
for hit in results["hits"]["hits"]:
    print(f"Log: {hit['_source']['log_text']}")
    print(f"Solution: {hit['_source']['resolution']}")