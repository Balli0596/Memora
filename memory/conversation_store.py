# memory/conversation_store.py

import chromadb
import uuid
from datetime import datetime, timezone


class ConversationStore:
    def get_user_interaction_count(self, user_id):

        result = self.collection.get(
            where={"user_id": user_id},
            include=["metadatas"]
        )

        return len(result["ids"])

    def get_recent_conversations(
        self,
        user_id,
        limit=5,
        offset=0
    ):

        result = self.collection.get(
            where={"user_id": user_id},
            include=["documents", "metadatas"]
        )

        records = list(zip(
            result["documents"],
            result["metadatas"]
        ))

        records.sort(
            key=lambda item: item[1]["timestamp"]
        )

        selected = records[offset:offset + limit]

        return [
            document for document, metadata in selected
        ]   
    def __init__(self, embedding_service):

        self.embedding_service = embedding_service

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"}
        )

    def save_conversation(
        self,
        user_id,
        conversation_id,
        question,
        answer
    ):

        document = (
            f"User: {question}\n"
            f"Assistant: {answer}"
        )

        embedding = self.embedding_service.generate_embedding(
            document
        )

        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[document],
            embeddings=[embedding],
            metadatas=[{
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()
            }]
        )

    def retrieve_memories(
        self,
        user_id,
        query,
        top_k=5
    ):

        if self.collection.count() == 0:
            return []

        query_embedding = (
            self.embedding_service.generate_embedding(query)
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"user_id": user_id},
            include=["documents", "metadatas", "distances"]
        )

        memories = []

        for document in results["documents"][0]:
            memories.append(document)

        return memories