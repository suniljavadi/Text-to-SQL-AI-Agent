import hashlib
import math
from .catalog import CATALOG

class SchemaRetriever:
    """Small dependency-light vector retriever; FAISS can replace this without changing its API."""
    def __init__(self, documents=None):
        self.documents = documents or CATALOG
        self.vectors = [self._vector(item["text"]) for item in self.documents]

    def _vector(self, text: str) -> list[float]:
        values = [0.0] * 128
        for token in text.lower().split():
            index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % len(values)
            values[index] += 1.0
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]

    def search(self, query: str, top_k: int = 6) -> list[dict]:
        query_vector = self._vector(query)
        scored = [(sum(a*b for a,b in zip(query_vector, vector)), item) for vector, item in zip(self.vectors, self.documents)]
        return [{**item, "score": round(score, 4)} for score, item in sorted(scored, key=lambda pair: pair[0], reverse=True)[:top_k]]

    def get_schema(self) -> list[dict]:
        return self.documents

    def get_business_definition(self, name: str) -> dict | None:
        name = name.lower().replace(" ", "_")
        return next((item for item in self.documents if item["name"] == name), None)
