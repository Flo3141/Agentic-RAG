"""Qdrant vector store implementation (Naive Version without Lock Handling)."""
import hashlib

import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
except ImportError:
    raise ImportError("Please install qdrant-client to use QdrantStore.")


class QdrantStore:
    def __init__(self, index_path: Optional[Path] = None, collection_name: str = "codebase", dim: int = 768):
        self.dim = dim
        self.collection_name = collection_name
        self.index_path = Path(index_path) if index_path else Path("../sample_project/qdrant_data")

        path_str = str(self.index_path)
        self.client = QdrantClient(path=path_str)

        # Ensure collection exists
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Properly close the Qdrant client."""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except Exception:
                pass

    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadata must have same length")

        points = []
        for i, (vec, meta) in enumerate(zip(vectors, metadatas)):
            # Qdrant requires unique IDs. --> We use Hashes of the symbol_id, so that we distinguish between
            # code snippets that are already embedded and new ones
            stable_id_str = meta["symbol_id"]  # z.B. "calculator.core.add"

            hash_val = hashlib.md5(stable_id_str.encode("utf-8")).hexdigest()
            point_id = str(uuid.UUID(hex=hash_val))

            points.append(models.PointStruct(
                id=point_id,
                vector=vec.tolist(),
                payload=meta
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        if query_vector.ndim > 1:
            query_vector = query_vector[0]  # Take first if batch

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=k
        )

        results = []
        for hit in response.points:
            item = hit.payload.copy()
            item['score'] = hit.score
            results.append(item)
        return results