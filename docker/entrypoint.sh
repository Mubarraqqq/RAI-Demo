#!/bin/sh
set -eu

cd /app

embed_flag=""
if [ "${BUILD_EMBEDDINGS:-0}" = "1" ]; then
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        embed_flag="--embed"
    else
        echo "[warn] BUILD_EMBEDDINGS=1 but OPENAI_API_KEY is not set; skipping embeddings."
    fi
fi

python build_corpus.py --bootstrap-db $embed_flag

exec python app.py
