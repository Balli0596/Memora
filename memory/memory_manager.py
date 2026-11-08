# memory/memory_manager.py

class MemoryManager:

    def __init__(
        self,
        conversation_store,
        profile_store,
        memory_extractor
    ):

        self.conversation_store = conversation_store
        self.profile_store = profile_store
        self.memory_extractor = memory_extractor

    def process_memory(self, user_id):

        total = self.conversation_store.get_user_interaction_count(
            user_id
        )

        processed = self.profile_store.get_questions_processed(
            user_id
        )

        memory_updated = False

        while total - processed >= 5:

            conversations = (
                self.conversation_store.get_recent_conversations(
                    user_id,
                    limit=5,
                    offset=processed
                )
            )

            existing_profile = self.profile_store.get_profile(
                user_id
            )

            updated_profile = (
                self.memory_extractor.extract_preferences(
                    conversations,
                    existing_profile
                )
            )

            processed += 5

            self.profile_store.save_profile(
                user_id=user_id,
                profile=updated_profile,
                questions_processed=processed
            )

            memory_updated = True

        return memory_updated