# core/embeddings.py

from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def generate_embedding(self, text: str):
        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]):
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()