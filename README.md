# Semantic Cache for LLM Applications

A semantic caching prototype designed to reduce unnecessary LLM API calls, response latency, and API usage by reusing answers to semantically similar questions.

Built using Python, Sentence Transformers, FAISS, and the Groq API.

## Problem

LLM-powered applications frequently receive repeated or semantically similar questions.

Sending every request to an LLM creates unnecessary API calls, increases response latency, and adds operational costs.

Traditional caching relies on exact string matching, meaning even slightly rephrased questions may trigger another LLM request.

## Solution

This project implements semantic caching using vector embeddings and similarity search.

Instead of comparing questions word-for-word, it converts them into numerical embeddings and searches for semantically similar cached questions.

- **Cache hit:** Return a previously generated answer when similarity, intent, and expiration checks pass.
- **Cache miss:** Send the question to the Groq API, generate an answer, and store it for potential reuse.

## Architecture

1. Receive a user question.
2. Generate a normalized embedding using Sentence Transformers.
3. Search the FAISS vector index using inner-product similarity.
4. Compare the similarity score against the configured threshold.
5. Apply a heuristic intent check to reduce incorrect cache matches.
6. Check whether the matched cache entry has expired.
7. Return the cached answer or call the Groq API.
8. Store successful LLM responses in the cache.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Sentence Transformers | Generate text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| FAISS | Vector similarity search |
| NumPy | Numerical operations |
| Groq API | Generate LLM responses |
| python-dotenv | Environment variable management |
| pytest | Automated testing |

## Key Features

- **Semantic similarity search:** Identifies similar questions using vector embeddings rather than exact text matching.
- **FAISS indexing:** Uses `IndexFlatIP` with normalized embeddings for cosine-similarity-based search.
- **Similarity threshold:** Configurable matching threshold, currently set to `0.80`.
- **Intent checking:** Uses a lightweight heuristic to distinguish definition, action, and general questions.
- **TTL-based expiration:** Cache entries expire after one hour.
- **Cache statistics:** Tracks total queries, cache hits, and cache misses.
- **LLM integration:** Uses Groq when a valid cached answer is unavailable.
- **Automated testing:** Covers cache hits, misses, intent mismatches, TTL expiration, and cache statistics.

## Evaluation

A custom evaluation dataset containing 10 question pairs was used to test different similarity thresholds.

The selected threshold was `0.80`, prioritizing fewer incorrect cache hits over maximizing cache reuse.

### Results at threshold 0.80

| Metric | Result |
|---|---:|
| Accuracy | 90% |
| Precision | 100% |
| Recall | 80% |
| False-hit rate | 0% |

These results are specific to the small evaluation dataset and are not production-level performance guarantees.

### Threshold Comparison

| Threshold | Accuracy | Precision | Recall |
|---|---:|---:|---:|
| 0.70 | 70% | 66.67% | 80% |
| 0.75 | 80% | 80% | 80% |
| 0.80 | 90% | 100% | 80% |
| 0.85 | 80% | 100% | 60% |
| 0.90 | 60% | 100% | 20% |

Evaluation also revealed that the embedding model struggled to associate the abbreviation "RAG" with "retrieval-augmented generation."

This demonstrates that threshold tuning alone cannot solve every semantic matching problem.

## Performance Benchmark

A small benchmark compared local cache lookup latency against direct Groq API response latency.

| Operation | Average Latency |
|---|---:|
| Cache lookup | 60.34 ms |
| Groq API response | 0.93 seconds |

**Observed speed improvement: approximately 15.35x.**

This benchmark used a limited number of requests. Actual performance varies with hardware, network conditions, embedding generation, and LLM response time.

## Automated Tests

Run the test suite from the project root:

```bash
python -m pytest -v
```

The test suite covers:

- Cache hit
- Cache miss
- Intent mismatch
- TTL expiration
- Cache statistics

## Project Structure

```text
semantic-cache-llm/
│
├── data/
│   ├── evaluation.json
│   └── faqs.json
│
├── src/
│   ├── benchmark.py
│   ├── cache.py
│   ├── embeddings.py
│   ├── evaluation.py
│   ├── llm.py
│   ├── main.py
│   └── __init__.py
│
├── tests/
│   └── test_cache.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone <https://github.com/sufipvt/semantic-cache-llm>
cd semantic-cache-llm
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Add your Groq API key:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key.

**Never commit your `.env` file or expose your API key publicly.**

### 5. Run the application

```powershell
python -m src.main
```

Enter questions in the terminal. Type `exit` to stop the application.

## Current Implementation Boundaries

- Cache entries are stored in memory and disappear when the application restarts.
- Expired entries are treated as cache misses, but their vectors are not physically removed from FAISS.
- Intent checking is heuristic-based and may reject valid matches or accept unsuitable ones.
- Embedding models may fail to recognize certain technical synonyms and abbreviations.
- Evaluation uses a small custom dataset.
- Benchmark results are based on a limited number of requests.
- The implementation is currently a single-process prototype, not a distributed caching service.

## Author

Built as a hands-on project to explore semantic caching, vector similarity search, LLM optimization, and evaluation techniques.