import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=False
)

try:
    r.execute_command(
        "FT.CREATE", "llm_cache_idx",
        "ON", "HASH",
        "PREFIX", "1", "llmcache:",
        "SCHEMA", "intent", "TAG",
        "question", "TEXT",
        "response", "TEXT",
        "embedding", "VECTOR", "FLAT", "6",
        "TYPE", "FLOAT32",
        "DIM", "384",
        "DISTANCE_METRIC", "COSINE"
    )

    print("Redis vector index created!")

except redis.exceptions.ResponseError as e:
    if "Index already exists" in str(e):
        print("Redis vector index already exists!")
    else:
        raise