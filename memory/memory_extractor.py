# memory/memory_extractor.py

import json
from pydantic import BaseModel, Field
from google.genai import types


class UserPreferences(BaseModel):

    likes: list[str] = Field(default_factory=list)

    dislikes: list[str] = Field(default_factory=list)

    interests: list[str] = Field(default_factory=list)

    favourite_genres: list[str] = Field(default_factory=list)

    preferred_pacing: list[str] = Field(default_factory=list)

    favourite_movies: list[str] = Field(default_factory=list)

    other_preferences: list[str] = Field(default_factory=list)


class MemoryExtractor:

    def __init__(self, llm):

        self.llm = llm

    def extract_preferences(
        self,
        conversations,
        existing_profile
    ):

        conversation_text = "\n\n".join(
            conversations
        )

        prompt = f"""
You are a user memory extraction engine.

Analyze the user's conversation and maintain
a structured user preference profile.

RECENT CONVERSATIONS:
{conversation_text}

EXISTING USER PROFILE:
{json.dumps(existing_profile, ensure_ascii=False)}

Extract and update:

1. Likes
2. Dislikes
3. Interests
4. Favourite genres
5. Preferred pacing
6. Favourite movies
7. Other preferences

IMPORTANT RULES:

- Extract only information supported by the conversation.
- Do not invent preferences.
- Do not confuse an assistant suggestion with a user preference.
- Retain existing information unless the user explicitly changes it.
- If a preference changes, update the old preference.
- Remove duplicate entries.
- Do not treat a single question as proof of a preference.
- Return only the updated profile.
"""

        response = self.llm.client.models.generate_content(
            model=self.llm.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=UserPreferences,
            )
        )

        if not response.text:
            raise ValueError("Empty memory extraction response")

        extracted = UserPreferences.model_validate_json(
            response.text
        )

        return extracted.model_dump()