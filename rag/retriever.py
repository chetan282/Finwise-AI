"""
retriever.py — query the knowledge base at run time.
"""
import os
import pickle
import functools

import faiss
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(__file__)
INDEX_PATH = os.path.join(HERE, "embeddings", "index.faiss")
CHUNKS_PATH = os.path.join(HERE, "embeddings", "chunks.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"


@functools.lru_cache(maxsize=1)
def _load():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("Index not built. Run:  python -m rag.build_index")
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    model = SentenceTransformer(MODEL_NAME)
    return index, chunks, model


def retrieve(query: str, k: int = 4) -> list:
    index, chunks, model = _load()
    vec = model.encode([query], normalize_embeddings=True)
    scores, ids = index.search(vec, k)
    return [chunks[i] for i in ids[0] if i != -1]
