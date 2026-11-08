# memory/profile_store.py

import chromadb
import json
from datetime import datetime, timezone


class ProfileStore:

    def __init__(self, embedding_service):

        self.embedding_service = embedding_service

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="user_profile_memory",
            metadata={"hnsw:space": "cosine"}
        )

    def get_profile(self, user_id):

        result = self.collection.get(
            ids=[user_id],
            include=["documents", "metadatas"]
        )

        if not result["documents"]:
            return {}

        return json.loads(result["documents"][0])

    def save_profile(
        self,
        user_id,
        profile,
        questions_processed
    ):

        document = json.dumps(profile, ensure_ascii=False)

        embedding = self.embedding_service.generate_embedding(
            document
        )

        self.collection.upsert(
            ids=[user_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[{
                "user_id": user_id,
                "questions_processed": questions_processed,
                "updated_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }]
        )

    def get_questions_processed(self, user_id):

        result = self.collection.get(
            ids=[user_id],
            include=["metadatas"]
        )

        if not result["metadatas"]:
            return 0

        return result["metadatas"][0].get(
            "questions_processed", 0
        )