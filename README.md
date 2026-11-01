# Semantic Cache for LLM Applications

A Python project demonstrating semantic caching for LLM applications using Sentence Transformers, FAISS, and the Groq API.

## Problem

LLM applications may repeatedly receive identical or semantically similar questions. Calling an LLM for every request can increase response latency and API usage.

## Solution

This project converts questions into normalized embeddings and uses FAISS to find semantically similar cached questions.

- **Cache hit:** Return the stored answer when the similarity score meets the configured threshold.
- **Cache miss:** Request an answer from Groq, then store the question and answer for potential reuse.

## Tech Stack

- Python
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS
- NumPy
- Groq API
- python-dotenv
- pytest

## Architecture

1. Receive a user question.
2. Generate its embedding.
3. Search the FAISS index.
4. Compare the best similarity score against the configured threshold.
5. Return the cached answer or call Groq.
6. Add successful LLM responses to the cache.

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd semantic-cache-llm
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` to Git.

### 5. Run the application

```powershell
python -m src.main
```

Type `exit` to stop the application.

## Current Limitations

- Cache entries exist only in memory and disappear when the application exits.
- The similarity threshold is a starting point and requires evaluation.
- Semantically similar questions may have different intents, potentially causing incorrect cache hits.
- The current implementation is a prototype, not a production-ready caching service.

## Planned Improvements

- Evaluate similarity thresholds and false cache hits.
- Add tests for cache behavior.
- Implement cache expiration and persistence.
- Improve error handling and reliability.
- Measure latency and cache hit rate.