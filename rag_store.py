import json
import math
import os
import sqlite3
from pathlib import Path

from openai import OpenAI

DB_PATH = Path("rag.db")
DOCS_DIR = Path("documents")
EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120


def _client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to a .env file or environment variable.")
    return OpenAI(api_key=api_key)


def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                UNIQUE(source, chunk_index)
            )
            """
        )
        conn.commit()


def _chunk_text(text):
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + CHUNK_SIZE)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def _embed(texts):
    response = _client().embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def ingest_documents():
    DOCS_DIR.mkdir(exist_ok=True)
    files = sorted(DOCS_DIR.glob("*.txt"))
    if not files:
        return

    with sqlite3.connect(DB_PATH) as conn:
        known_sources = {
            row[0] for row in conn.execute("SELECT DISTINCT source FROM chunks").fetchall()
        }

    for path in files:
        if path.name in known_sources:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks = _chunk_text(text)
        if not chunks:
            continue
        embeddings = _embed(chunks)
        with sqlite3.connect(DB_PATH) as conn:
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                conn.execute(
                    "INSERT OR REPLACE INTO chunks(source, chunk_index, text, embedding) VALUES (?, ?, ?, ?)",
                    (path.name, index, chunk, json.dumps(embedding)),
                )
            conn.commit()


def _cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_chunks(question, top_k=4, min_score=0.20):
    question_embedding = _embed([question])[0]
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT source, chunk_index, text, embedding FROM chunks").fetchall()

    scored = []
    for source, chunk_index, text, embedding_json in rows:
        embedding = json.loads(embedding_json)
        score = _cosine_similarity(question_embedding, embedding)
        if score >= min_score:
            scored.append(
                {
                    "source": source,
                    "chunk_index": chunk_index,
                    "text": text,
                    "score": score,
                }
            )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]
