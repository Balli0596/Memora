# services/chat_service.py

import logging


class ChatService:

    def __init__(
        self,
        llm,
        conversation_store,
        profile_store,
        memory_manager
    ):

        self.llm = llm
        self.conversation_store = conversation_store
        self.profile_store = profile_store
        self.memory_manager = memory_manager

    def chat(
        self,
        user_id,
        conversation_id,
        question,
        history
    ):

        # 1. Retrieve previous conversations
        memories = self.conversation_store.retrieve_memories(
            user_id=user_id,
            query=question,
            top_k=5
        )

        # 2. Retrieve long-term user profile
        profile = self.profile_store.get_profile(user_id)

        if profile:
            memories.insert(
                0,
                "STORED USER PREFERENCES:\n" + str(profile)
            )

        # 3. Generate answer
        answer = self.llm.generate_response(
            question=question,
            memories=memories,
            history=history
        )

        # 4. Save question and answer
        self.conversation_store.save_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            question=question,
            answer=answer
        )

        # 5. Check whether memory extraction is required
        memory_updated = False

        try:
            memory_updated = self.memory_manager.process_memory(
                user_id
            )

        except Exception:
            logging.exception(
                "Memory extraction failed for user %s",
                user_id
            )

        return answer, memory_updated