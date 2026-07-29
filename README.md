# BRDGE RAG Learning Assistant

This repository contains a small Flask-based prototype for the BRDGE RAG work test.

It is intentionally built around the real `RAG Docs` export in this workspace rather than an idealized corpus. The system uses:

- a canonical registry to map the 31 brief-defined sub-facets to real files
- an offline corpus build step that extracts documents, chunks, and optional embeddings
- SQLite for asset, chunk, embedding, and session storage
- a conversation engine that holds the active sub-facet and returns grounded assets only
- a Docker path that bootstraps the corpus and starts the app with one command

## What It Does

The prototype supports:

- selecting one of the brief-defined sub-facets
- holding the conversation on that chosen area
- blocking early pathway generation until a minimum number of coaching turns have happened
- returning grounded Learning Pathway assets from the real corpus
- grounding coaching replies on retrieved passages from the active sub-facet
- semantic retrieval with OpenAI `text-embedding-3-small` when embeddings are built
- lexical retrieval fallback when embeddings are unavailable
- optional LLM-assisted intent detection and coaching phrasing when `OPENAI_API_KEY` is set
- handling missing asset types honestly
- persisting conversation session state

The current implementation actively uses:

- slide assets
- worksheet/exercise assets
- report consent state

If `OPENAI_API_KEY` is present, the app also uses `OPENAI_MODEL` and `OPENAI_BASE_URL` to enable the dynamic LLM layer. Without that key, it falls back to the deterministic rules covered by the tests.

## Docker First

The reproducible path is Docker Compose:

```bash
docker compose up --build
```

That command:

- builds the image
- bootstraps the corpus into `data/processed`
- starts the Flask app on `http://localhost:5000`

Optional embeddings and dynamic LLM behavior:

```bash
OPENAI_API_KEY=your_api_key_here BUILD_EMBEDDINGS=1 docker compose up --build
```

The container will still run without the key. In that case it uses lexical retrieval and the deterministic fallback flow.

Important corpus constraint:

- the supplied `RAG Docs` export does not clearly contain distinct transcript assets
- the supplied `RAG Docs` export does not clearly contain distinct post assets

Those asset types are therefore treated as unavailable rather than invented.

For the supporting rationale behind that decision, see:

- `docs/corpus_compliance_audit.md`
- `docs/architecture_note.md`

## Project Layout

```text
app.py
build_corpus.py
engine.py
storage.py
requirements.txt
.dockerignore
Dockerfile
docker-compose.yml
docker/
  entrypoint.sh
.env.example
README.md
docs/
  corpus_compliance_audit.md
data/
  processed/
    corpus_registry.json
    documents.jsonl
    chunks.jsonl
    embeddings.jsonl
    manifest.db
tests/
  test_app.py
  test_corpus.py
RAG Docs/
```

## Main Files

- `data/processed/corpus_registry.json`
  The source-of-truth mapping from official sub-facet names to real files in `RAG Docs`.

- `build_corpus.py`
  Reads the registry, extracts text from mapped files, writes normalized document/chunk records, and can generate OpenAI embeddings.

- `storage.py`
  Stores normalized assets, chunks, optional embeddings, and session state in SQLite.

- `engine.py`
  Contains the conversation flow, area hold, switch logic, safety guardrails, and Learning Pathway generation.

- `app.py`
  Exposes the engine through a minimal Flask API.

- `docs/architecture_note.md`
  Submission-facing explanation of the system design, corpus assumptions, demo flow, and trade-offs.

## Setup

Docker is the recommended path. If you want to run locally instead, use the steps below.

Create and use the local virtual environment:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Create a local environment file for secrets:

```bash
cp .env.example .env
```

Then edit `.env` and set:

```text
OPENAI_API_KEY=your_api_key_here
# optional:
# OPENAI_MODEL=chat-latest
# OPENAI_BASE_URL=https://api.openai.com/v1
```

The real `.env` file is ignored by git so the API key is not committed.

## Build The Corpus

Rebuild the normalized documents from the registry:

```bash
venv/bin/python build_corpus.py
```

This writes:

- `data/processed/documents.jsonl`
- `data/processed/chunks.jsonl`

To also build semantic embeddings with OpenAI `text-embedding-3-small`, make sure `.env` contains `OPENAI_API_KEY`, then run:

```bash
venv/bin/python build_corpus.py --embed
```

This also writes:

- `data/processed/embeddings.jsonl`

Load the normalized documents into SQLite:

```bash
venv/bin/python - <<'PY'
from storage import Storage

store = Storage("data/processed/manifest.db")
store.initialize()
inserted = store.load_documents("data/processed/documents.jsonl")
chunks = store.load_chunks("data/processed/chunks.jsonl")
print(f"Loaded {inserted} documents")
print(f"Loaded {chunks} chunks")
PY
```

If you generated embeddings, load them too:

```bash
venv/bin/python - <<'PY'
from storage import Storage

store = Storage("data/processed/manifest.db")
store.initialize()
embeddings = store.load_embeddings("data/processed/embeddings.jsonl")
print(f"Loaded {embeddings} embeddings")
PY
```

This writes:

- `data/processed/manifest.db`

## Run The App

Start the Flask app:

```bash
venv/bin/python app.py
```

The app exposes:

- `GET /health`
- `GET /`
- `POST /start`
- `POST /consent`
- `POST /chat`
- `POST /resume`

If you are using Docker Compose, the app is already running after `docker compose up --build`.

## Smooth Demo Flow

If you want the cleanest end-to-end walkthrough, use this sequence:

1. Start a session
2. Set consent to `false`
3. Choose a specific sub-facet such as `work life balance`
4. Give two short coaching replies
5. Ask for the pathway

Example:

```bash
curl -X POST http://127.0.0.1:5000/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user"}'

curl -X POST http://127.0.0.1:5000/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","consent":false}'

curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"I want help with work life balance"}'

curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"It is getting harder to switch off after work"}'

curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"I keep feeling guilty when I stop working"}'

curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"show me the pathway"}'
```

Expected outcome:

- the assistant stays on `Work-life balance`
- it does not jump early to the pathway
- it returns the mapped slide and worksheet files for that sub-facet only

## Example Requests

Start a session:

```bash
curl -X POST http://127.0.0.1:5000/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user"}'
```

Set consent:

```bash
curl -X POST http://127.0.0.1:5000/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","consent":false}'
```

Choose an area:

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"I want help with work life balance"}'
```

Request the pathway after enough turns:

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","message":"show me the pathway"}'
```

## Run Tests

Run the automated test suite:

```bash
venv/bin/python -m unittest discover -s tests -v
```

## Current Design Choices

This implementation is intentionally small.

- The conversation flow is application-controlled, not LLM-controlled.
- The active sub-facet is held in session state.
- Retrieval prefers stored OpenAI embeddings and falls back to lexical chunk search.
- Retrieval is always scoped to the active sub-facet through the local asset store.
- The app returns only real files that were mapped in the registry.
- Missing asset types are reported honestly instead of being invented.

## Trade-Offs

- I chose a registry-first design because the supplied corpus has naming drift and uneven asset structure.
- I prioritized strict sub-facet isolation over broader retrieval flexibility.
- I use `text-embedding-3-small` for semantic retrieval when embeddings are built, while keeping lexical retrieval as a fallback.
- I load `OPENAI_API_KEY` from `.env` locally, while keeping `.env.example` as a safe template for submission.
- I kept the Flask app thin and pushed flow control into application logic so the state machine is easy to inspect and test.
- I treated missing transcripts/posts as explicit gaps in the corpus instead of fabricating substitutes.

## Known Limitations

- No distinct transcript assets are currently mapped from the provided export.
- No distinct post assets are currently mapped from the provided export.
- The report branch uses lightweight report-style reflection rather than deep personalized report interpretation.
- Embedding generation requires `OPENAI_API_KEY`; without it, the app falls back to lexical chunk search.
- The safety layer is rule-based rather than model-assisted.

## Corpus Audit

The current corpus audit is documented here:

- `docs/corpus_compliance_audit.md`
- `docs/architecture_note.md`

Those notes explain:

- what assets are present
- what asset types are missing
- where naming drift exists
- why the registry layer is necessary
