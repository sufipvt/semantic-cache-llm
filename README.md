# Redis Semantic Cache for LLM Applications

A semantic caching system for LLM applications that uses **Redis Vector Search** to identify semantically similar questions and reuse previously generated responses instead of repeatedly calling an LLM.

The project combines Sentence Transformers, Redis, and the Groq API to reduce response latency and unnecessary LLM calls.

## Overview

Traditional caching relies on exact matches. However, users often ask the same question using different wording.

For example:

- "What is machine learning?"
- "Explain machine learning."
- "Can you define ML?"

A traditional cache may treat these as different queries.

This project uses semantic similarity to generate embeddings and search for similar questions stored in Redis. If a sufficiently similar question is found, its cached response is returned. Otherwise, the application calls the Groq LLM and stores the new response.

## Architecture

```text
                 User Question
                       |
                       v
                FastAPI Endpoint
                       |
                       v
               Validate Question
                       |
                       v
                Check Redis Health
                       |
                       v
              Generate Embedding
              Sentence Transformers
                       |
                       v
             Redis Vector Search
                       |
                 Intent Filter
                       |
                       v
              KNN Similarity Search
                       |
                 Is Cache Hit?
                  /        \
                Yes         No
                 |           |
                 v           v
           Return Cached   Call Groq LLM
             Response          |
                               v
                         Generate Answer
                               |
                               v
                         Store in Redis
                               |
                               v
                         Return Answer
```

If Redis is unavailable, the application skips caching and calls the Groq LLM directly.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| LLM Provider | Groq API |
| LLM Model | `openai/gpt-oss-120b` |
| Embedding Model | `all-MiniLM-L6-v2` |
| Vector Database | Redis Stack |
| Vector Search | Redis Vector Search |
| Similarity Metric | Cosine Distance |
| Data Storage | Redis Hash |
| Testing | Pytest |
| API Testing | HTTPX |
| Containerization | Docker |

## Key Features

### 1. Semantic Caching

Uses Sentence Transformers to convert questions into 384-dimensional embeddings.

Semantically similar questions can retrieve previously generated responses even when their wording differs.

### 2. Redis Vector Search

Stores question embeddings in Redis Hashes and searches them using Redis Vector Search.

The application uses K-Nearest Neighbors (KNN) to identify the closest matching question.

### 3. Intent-Based Filtering

Before vector search, questions are classified using a rule-based heuristic intent classifier.

Supported categories:

- Comparison
- Troubleshooting
- Procedure
- Definition
- General

Redis applies an intent TAG filter during vector search to restrict candidate matches.

### 4. Similarity Threshold

The current cache similarity threshold is:

```python
THRESHOLD = 0.20
```

A result is considered a cache hit when its cosine distance is less than or equal to the threshold.

The threshold is experimental and has not been calibrated across a broad evaluation dataset.

### 5. TTL-Based Expiration

Cached entries automatically expire after:

```python
TTL = 3600  # 1 hour
```

This prevents cached responses from remaining indefinitely.

### 6. Redis Fallback

If Redis is unavailable, the application bypasses caching and calls the Groq API directly.

This allows the application to continue answering questions without Redis, although caching benefits are temporarily unavailable.

### 7. Cache Statistics

Tracks:

- Total queries
- Cache hits
- Cache misses
- Cache hit rate

Statistics are maintained in application memory and reset when the application restarts.

## Project Structure

```text
semantic-cache-llm/
│
├── benchmarks/
│   └── benchmark.py
│
├── data/
│   ├── evaluation.json
│   └── faqs.json
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── cache.py
│   ├── create_index.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── llm.py
│   └── main.py
│
├── tests/
│   ├── test_api.py
│   └── test_intent.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Getting Started

### Prerequisites

Install the following:

- Python 3.12+
- Docker
- Redis Stack
- Groq API key

### 1. Clone the Repository

```bash
git clone https://github.com/sufipvt/semantic-cache-llm.git

cd semantic-cache-llm
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```cmd
copy .env.example .env
```

Add your Groq API key and configure the environment variables using the names defined in `.env.example`.

Never commit your actual `.env` file or API credentials.

### 5. Start Redis Stack

Run Redis Stack using Docker:

```bash
docker run -d \
  --name semantic-redis \
  -p 6379:6379 \
  redis/redis-stack:latest
```

Verify the Redis connection:

```bash
docker exec -it semantic-redis redis-cli
```

Inside the Redis CLI:

```redis
PING
```

Expected response:

```text
PONG
```

### 6. Create the Redis Vector Index

Run the index initialization script:

```bash
python -m src.create_index
```

The script creates the Redis vector index with:

| Configuration | Value |
|---|---|
| Index name | `llm_cache_idx` |
| Key prefix | `llmcache:` |
| Storage type | HASH |
| Vector dimension | 384 |
| Algorithm | FLAT |
| Distance metric | COSINE |
| Intent field | TAG |

If the index already exists, the script reports that instead of attempting to recreate it.

### 7. Start the FastAPI Server

```bash
uvicorn src.api:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### POST `/ask`

Submit a question to the application.

Request:

```json
{
  "question": "What is machine learning?"
}
```

Response:

```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a branch of artificial intelligence..."
}
```

The answer may come from Redis or the Groq LLM, depending on whether a suitable cached result is found.

### GET `/stats`

Returns cache statistics.

Example:

```json
{
  "total_queries": 10,
  "cache_hits": 6,
  "cache_misses": 4,
  "hit_rate": 0.6
}
```

### GET `/health`

Checks API and Redis health.

Example:

```json
{
  "api": "healthy",
  "redis": "connected",
  "cache": "available",
  "status": "healthy"
}
```

## Running Tests

Run the test suite:

```bash
python -m pytest -v
```

Current test coverage includes:

- FastAPI health endpoint
- Cache statistics endpoint
- Question submission endpoint
- Empty and whitespace-only question validation
- Rule-based intent classification

Latest verified result:

```text
14 passed
```

## Performance Benchmark

The project includes a benchmark comparing direct Groq LLM calls against Redis semantic cache lookups.

Run:

```bash
python -m benchmarks.benchmark
```

### Latest Benchmark Results

| Metric | Direct LLM | Redis Cache |
|---|---:|---:|
| Average latency | 0.6050 s | 0.0648 s |
| Median latency | 0.5873 s | 0.0527 s |
| Minimum latency | 0.3051 s | 0.0283 s |
| Maximum latency | 1.4057 s | 0.1250 s |

**Measured speed improvement: 9.34x**

Additional results:

- Iterations: 10
- LLM calls avoided: 10
- Cache correctness: True

### Benchmark Methodology

The benchmark compares 10 direct Groq requests against 10 Redis cache hits for the same question.

The embedding model and Redis search are warmed up before timing.

Cache latency includes embedding generation and Redis vector search.

**Important:** These results represent a repeated-query, cache-friendly workload. Actual performance will vary depending on query distribution, cache hit rate, network conditions, and LLM response times. The 9.34x result should not be interpreted as a universal performance guarantee.

## Current Limitations

- Intent classification uses rule-based heuristics rather than a trained ML model.
- The similarity threshold is experimental and requires broader evaluation.
- Cache statistics are stored in application memory and reset after restart.
- The benchmark uses repeated identical questions rather than a representative production workload.
- Redis fallback is implemented, but not every possible failure scenario has been independently tested.
- The current implementation uses a single Redis instance and does not include distributed deployment or authentication configuration.

## Future Improvements

Potential directions for further development:

- Evaluate and calibrate similarity thresholds using a larger dataset.
- Add persistent cache analytics.
- Benchmark using realistic query distributions.
- Explore more advanced cache invalidation strategies.
- Add monitoring and observability.
- Evaluate performance under concurrent requests.

## Author

**Sufiyan Rizvi**

B.Tech Computer Science and Engineering (AI & ML)

GitHub: https://github.com/sufipvt

---

If you find this project useful, consider giving the repository a star.