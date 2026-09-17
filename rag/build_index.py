"""
build_index.py — chunks knowledge docs, embeds them, saves a FAISS index.
Run:  python -m rag.build_index
"""
import os
import glob
import pickle

import faiss
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(__file__)
KB_DIR = os.path.join(HERE, "knowledge_base")
INDEX_PATH = os.path.join(HERE, "embeddings", "index.faiss")
CHUNKS_PATH = os.path.join(HERE, "embeddings", "chunks.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"


def chunk_text(text: str) -> list:
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]


def build():
    chunks = []
    for path in glob.glob(os.path.join(KB_DIR, "*.md")):
        source = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            for para in chunk_text(f.read()):
                chunks.append({"text": para, "source": source})

    print(f"Loaded {len(chunks)} chunks from {KB_DIR}")

    model = SentenceTransformer(MODEL_NAME)
    vectors = model.encode([c["text"] for c in chunks], normalize_embeddings=True)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"Saved FAISS index ({index.ntotal} vectors) -> {INDEX_PATH}")


if __name__ == "__main__":
    build()
