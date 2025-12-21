"""Embedding interface using sentence-transformers."""
from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class Embedder:
    def __init__(self, model_name: str = "intfloat/e5-base-v2", device: str = "cpu"):
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers not installed")
        self.model = SentenceTransformer(model_name, device=device)
        self._cache = {}

    def encode(self, texts: List[str]) -> np.ndarray:
        # TODO Maybe make the embeddings persistent on the disk, not only in memory?
        to_encode = []
        indices = []
        results = [None] * len(texts)

        for i, text in enumerate(texts):
            if text in self._cache:
                results[i] = self._cache[text]
            else:
                to_encode.append(text)
                indices.append(i)

        if to_encode:
            embeddings = self.model.encode(to_encode, convert_to_numpy=True)
            for idx, emb in zip(indices, embeddings):
                self._cache[texts[idx]] = emb
                results[idx] = emb

        return np.vstack(results)