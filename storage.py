#!/usr/bin/env python3

import json
import math
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class Storage:
    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "does",
        "do",
        "for",
        "from",
        "how",
        "i",
        "if",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "about",
        "say",
        "so",
        "that",
        "the",
        "their",
        "them",
        "there",
        "they",
        "this",
        "to",
        "what",
        "with",
        "you",
        "your",
    }

    def __init__(self, db_path: str = "data/processed/manifest.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    document_id TEXT PRIMARY KEY,
                    subfacet_id TEXT NOT NULL,
                    canonical_name TEXT NOT NULL,
                    facet TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    source_filename TEXT NOT NULL,
                    extension TEXT NOT NULL,
                    text TEXT NOT NULL,
                    text_length INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    user_id TEXT PRIMARY KEY,
                    consent INTEGER DEFAULT 0,
                    report_used INTEGER DEFAULT 0,
                    current_subfacet_id TEXT,
                    current_subfacet_name TEXT,
                    turn_count INTEGER DEFAULT 0,
                    plan_generated INTEGER DEFAULT 0,
                    pathway_offered INTEGER DEFAULT 0,
                    last_subfacet_id TEXT,
                    history_json TEXT NOT NULL DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    subfacet_id TEXT NOT NULL,
                    canonical_name TEXT NOT NULL,
                    facet TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    source_filename TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    text_length INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chunk_embeddings (
                    chunk_id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    embedding_json TEXT NOT NULL
                );
                """
            )

            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(sessions)").fetchall()
            }
            if "pathway_offered" not in columns:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN pathway_offered INTEGER DEFAULT 0"
                )

    def load_documents(self, documents_path: str = "data/processed/documents.jsonl") -> int:
        path = Path(documents_path)
        if not path.exists():
            raise FileNotFoundError(f"Documents file not found: {path}")

        inserted = 0
        with self.connect() as conn:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    document = json.loads(line)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO assets (
                            document_id,
                            subfacet_id,
                            canonical_name,
                            facet,
                            asset_type,
                            source_path,
                            source_filename,
                            extension,
                            text,
                            text_length
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            document["document_id"],
                            document["subfacet_id"],
                            document["canonical_name"],
                            document["facet"],
                            document["asset_type"],
                            document["source_path"],
                            document["source_filename"],
                            document["extension"],
                            document["text"],
                            document["text_length"],
                        ),
                    )
                    inserted += 1
        return inserted

    def load_embeddings(
        self,
        embeddings_path: str = "data/processed/embeddings.jsonl",
    ) -> int:
        path = Path(embeddings_path)
        if not path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {path}")

        inserted = 0
        with self.connect() as conn:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO chunk_embeddings (
                            chunk_id,
                            model,
                            embedding_json
                        ) VALUES (?, ?, ?)
                        """,
                        (
                            record["chunk_id"],
                            record["model"],
                            json.dumps(record["embedding"]),
                        ),
                    )
                    inserted += 1
        return inserted

    def load_chunks(self, chunks_path: str = "data/processed/chunks.jsonl") -> int:
        path = Path(chunks_path)
        if not path.exists():
            raise FileNotFoundError(f"Chunks file not found: {path}")

        inserted = 0
        with self.connect() as conn:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    chunk = json.loads(line)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO chunks (
                            chunk_id,
                            document_id,
                            subfacet_id,
                            canonical_name,
                            facet,
                            asset_type,
                            source_path,
                            source_filename,
                            chunk_index,
                            text,
                            text_length
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            chunk["chunk_id"],
                            chunk["document_id"],
                            chunk["subfacet_id"],
                            chunk["canonical_name"],
                            chunk["facet"],
                            chunk["asset_type"],
                            chunk["source_path"],
                            chunk["source_filename"],
                            int(chunk["chunk_index"]),
                            chunk["text"],
                            int(chunk["text_length"]),
                        ),
                    )
                    inserted += 1
        return inserted

    def list_assets_for_subfacet(self, subfacet_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM assets
                WHERE subfacet_id = ?
                ORDER BY
                    CASE asset_type
                        WHEN 'slides' THEN 1
                        WHEN 'worksheets' THEN 2
                        WHEN 'transcripts' THEN 3
                        WHEN 'posts' THEN 4
                        ELSE 5
                    END,
                    source_filename
                """,
                (subfacet_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_asset(self, document_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM assets WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return dict(row) if row else None

    def search_chunks(
        self,
        subfacet_id: str,
        query: str,
        limit: int = 3,
        min_score: float = 1.0,
    ) -> list[dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM chunks
                WHERE subfacet_id = ?
                """,
                (subfacet_id,),
            ).fetchall()

        scored: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            chunk = dict(row)
            score = self._score_chunk(query_tokens, chunk["text"])
            if score >= min_score:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**chunk, "score": score} for score, chunk in scored[:limit]]

    def search_embedding_chunks(
        self,
        subfacet_id: str,
        query_embedding: list[float],
        limit: int = 3,
        min_score: float = 0.2,
    ) -> list[dict[str, Any]]:
        if not query_embedding:
            return []

        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT chunks.*, chunk_embeddings.model, chunk_embeddings.embedding_json
                FROM chunks
                JOIN chunk_embeddings ON chunks.chunk_id = chunk_embeddings.chunk_id
                WHERE chunks.subfacet_id = ?
                """,
                (subfacet_id,),
            ).fetchall()

        scored: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            chunk = dict(row)
            embedding = json.loads(chunk.pop("embedding_json"))
            score = self._cosine_similarity(query_embedding, embedding)
            if score >= min_score:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**chunk, "score": score, "retrieval": "embedding"} for score, chunk in scored[:limit]]

    def get_or_create_session(self, user_id: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row:
                return self._row_to_session(row)

            conn.execute(
                """
                INSERT INTO sessions (
                    user_id,
                    history_json
                ) VALUES (?, '[]')
                """,
                (user_id,),
            )
            row = conn.execute(
                "SELECT * FROM sessions WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return self._row_to_session(row)

    def delete_session(self, user_id: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ?",
                (user_id,),
            )

    def save_session(self, session: dict[str, Any]) -> None:
        history = session.get("history", [])
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    user_id,
                    consent,
                    report_used,
                    current_subfacet_id,
                    current_subfacet_name,
                    turn_count,
                    plan_generated,
                    pathway_offered,
                    last_subfacet_id,
                    history_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    consent = excluded.consent,
                    report_used = excluded.report_used,
                    current_subfacet_id = excluded.current_subfacet_id,
                    current_subfacet_name = excluded.current_subfacet_name,
                    turn_count = excluded.turn_count,
                    plan_generated = excluded.plan_generated,
                    pathway_offered = excluded.pathway_offered,
                    last_subfacet_id = excluded.last_subfacet_id,
                    history_json = excluded.history_json
                """,
                (
                    session["user_id"],
                    int(bool(session.get("consent", False))),
                    int(bool(session.get("report_used", False))),
                    session.get("current_subfacet_id"),
                    session.get("current_subfacet_name"),
                    int(session.get("turn_count", 0)),
                    int(bool(session.get("plan_generated", False))),
                    int(bool(session.get("pathway_offered", False))),
                    session.get("last_subfacet_id"),
                    json.dumps(history),
                ),
            )

    def append_message(self, user_id: str, role: str, text: str) -> dict[str, Any]:
        session = self.get_or_create_session(user_id)
        history = session.get("history", [])
        history.append({"role": role, "text": text})
        session["history"] = history
        self.save_session(session)
        return session

    def _row_to_session(self, row: sqlite3.Row | None) -> dict[str, Any]:
        if row is None:
            raise ValueError("Expected a session row but received none")
        data = dict(row)
        data["consent"] = bool(data["consent"])
        data["report_used"] = bool(data["report_used"])
        data["plan_generated"] = bool(data["plan_generated"])
        data["pathway_offered"] = bool(data.get("pathway_offered", 0))
        data["history"] = json.loads(data.pop("history_json"))
        return data

    def _tokenize(self, text: str) -> list[str]:
        normalized = text.lower().replace("&", " and ")
        return [
            token
            for token in re.findall(r"[a-z0-9]+", normalized)
            if token not in self.STOPWORDS and len(token) > 1
        ]

    def _score_chunk(self, query_tokens: list[str], chunk_text: str) -> float:
        chunk_tokens = self._tokenize(chunk_text)
        if not chunk_tokens:
            return 0.0

        chunk_counts: dict[str, int] = {}
        for token in chunk_tokens:
            chunk_counts[token] = chunk_counts.get(token, 0) + 1

        score = 0.0
        unique_matches = 0
        for token in query_tokens:
            freq = chunk_counts.get(token, 0)
            if freq:
                unique_matches += 1
                score += 1.0 + math.log1p(freq)

        normalized_query = " ".join(query_tokens)
        normalized_chunk = " ".join(chunk_tokens)
        if unique_matches < 2 and normalized_query not in normalized_chunk:
            return 0.0

        if normalized_query and normalized_query in normalized_chunk:
            score += 3.0

        if unique_matches >= max(2, len(set(query_tokens)) // 2):
            score += 1.5

        return score

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if len(left) != len(right) or not left:
            return 0.0

        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)
