# Architecture Note

## Goal

Build a small, defensible prototype for the BRDGE RAG work test that:

- keeps the assistant on one chosen sub-facet
- grounds pathway recommendations in real files only
- handles the supplied corpus honestly, including missing asset types
- remains simple enough to explain clearly in a follow-up walkthrough

## Plain-English System Overview

The system has four moving parts:

1. `corpus_registry.json`
   This is the translation layer between the official sub-facet names in the brief and the real filenames in `RAG Docs`.

2. `build_corpus.py`
   This extracts text from the mapped files and creates:
   - document records
   - chunk records
   - optional OpenAI embedding records

3. `storage.py`
   This stores:
   - asset records
   - chunk records
   - embedding records
   - user sessions

4. `engine.py`
   This controls the conversation:
   - consent handling
   - sub-facet selection
   - sub-facet hold
   - explicit switching
   - coaching turns
   - grounded Learning Pathway output
   - safety and refusal behavior

Runtime configuration is intentionally minimal. Local secrets live in `.env`, using `.env.example` as the safe template. The app and corpus builder load that file automatically so `OPENAI_API_KEY` is available for `text-embedding-3-small` without hard-coding secrets.
If the key is present, the conversation engine can also use a dynamic LLM layer for intent detection and coaching phrasing. That layer is optional and never replaces the session state machine.

## Why The Registry Layer Exists

The corpus is real-world messy rather than cleanly labeled.

Examples:

- `Avoiding procrastination` appears as `Procrastination`
- `Managing emotions` appears as `Understanding and Managing Emotions`
- `Self-awareness` appears once as `Self Awarenesss`
- `Taking regular exercise` appears under the misspelled folder `Taking Regular Ecercise`

If the assistant used raw filenames directly, retrieval and pathway output would be brittle. The registry fixes that by giving every official sub-facet one clean source-of-truth record.

## Corpus Reality Versus Brief Assumptions

The brief describes a corpus shape that includes:

- video transcript(s)
- slide text
- worksheet/exercises
- 2–3 posts per sub-facet

The supplied `RAG Docs` export clearly supports:

- slides
- worksheets/exercises
- sample report files

The supplied export does **not** clearly provide:

- distinct transcript assets
- distinct post assets

Design decision:

- treat those asset types as unavailable
- do not invent substitute resources
- document the gap clearly

## Retrieval Design

The current retrieval path is:

1. the user selects a sub-facet
2. the session stores that sub-facet as active
3. the engine searches only chunks from that sub-facet
4. if OpenAI embeddings have been built, the engine uses semantic search with `text-embedding-3-small`
5. if embeddings are unavailable, the engine falls back to lexical chunk search
6. the response is grounded on the top matching chunk passages
7. the Learning Pathway is assembled from mapped asset files for that same sub-facet

This is deliberately conservative. The main goal is to prevent cross-sub-facet leakage.

## Conversation Design

The assistant does not decide its own flow. The application does.

Session state tracks:

- consent
- report usage
- current sub-facet
- last sub-facet
- turn count
- whether a pathway has already been generated
- conversation history

That makes the conversation behavior predictable and testable.

## Demo Flow

For the cleanest demonstration:

1. Start a session
2. Set consent to `false`
3. Choose `Work-life balance`
4. Give two short replies about the problem
5. Ask for the pathway

This reliably shows:

- area selection
- area hold
- minimum coaching turns before pathway generation
- grounded file output from the correct sub-facet

## Trade-Offs

- I favored strict sub-facet isolation over broader search flexibility.
- I added embedding retrieval with `text-embedding-3-small`, while preserving lexical retrieval as a fallback when API credentials or embedding records are unavailable.
- I used `.env` for local OpenAI credentials and kept only `.env.example` in the repository.
- I added a Docker Compose path so the corpus bootstrap and app startup can happen with one command on any machine with Docker.
- I kept the Flask API thin so the logic remains in one engine module.
- I made the LLM layer optional so the prototype still runs and tests offline even without API calls.
- I accepted a simpler report branch rather than over-claiming personalized report understanding.
- I documented corpus gaps instead of hiding them with fabricated assets.

## Current Gaps

The prototype is stronger than a simple file lookup, but it is still not the full end-state described by the brief.

Main remaining gaps:

- embedding generation requires `OPENAI_API_KEY`
- the dynamic LLM layer also requires `OPENAI_API_KEY`
- the report branch is lightweight rather than deeply personalized
- the safety layer is rule-based rather than model-assisted
- the Docker path still assumes the `RAG Docs` corpus is available in the build context

Those are deliberate scope cuts rather than accidental omissions.
