# app.py

import streamlit as st
import uuid
import os

from dotenv import load_dotenv

from core.embeddings import EmbeddingService
from core.llm import GeminiService
from memory.conversation_store import ConversationStore
from services.chat_services import ChatService
from memory.profile_store import ProfileStore
from memory.memory_extractor import MemoryExtractor
from memory.memory_manager import MemoryManager

load_dotenv()

st.set_page_config(
    page_title="Memora AI",
    page_icon="🧠",
    layout="wide"
)


# Initialize backend services only once
@st.cache_resource
def initialize_services():

    embedding_service = EmbeddingService()

    conversation_store = ConversationStore(
        embedding_service
    )

    profile_store = ProfileStore(
        embedding_service
    )

    llm = GeminiService()

    memory_extractor = MemoryExtractor(llm)

    memory_manager = MemoryManager(
        conversation_store,
        profile_store,
        memory_extractor
    )

    chat_service = ChatService(
        llm,
        conversation_store,
        profile_store,
        memory_manager
    )

    return (
        chat_service,
        conversation_store,
        profile_store
    )
try:

    (
        chat_service,
        conversation_store,
        profile_store
    ) = initialize_services()

except Exception as e:

    st.error(f"Initialization error: {e}")
    st.stop()

try:
    chat_service, conversation_store, profile_store = initialize_services()
except Exception as e:
    st.error(f"Initialization error: {e}")
    st.stop()


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "user_id" not in st.session_state:
    st.session_state.user_id = "user_101"


# Sidebar
with st.sidebar:

    st.title("🧠 Memora AI")

    st.caption("Your AI with long-term memory")

    st.text_input(
        "User ID",
        key="user_id"
    )

    st.divider()

    st.subheader("Memory Dashboard")

    st.metric(
        "Questions asked",
        st.session_state.question_count
    )
    stored_count = conversation_store.get_user_interaction_count(
        st.session_state.user_id
    )

    st.metric(
        "Stored interactions",
        stored_count
    )

    st.caption(
        f"Conversation ID: "
        f"{st.session_state.conversation_id[:8]}"
    )

    if st.button("New Conversation", use_container_width=True):

        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.conversation_id = str(uuid.uuid4())

        st.rerun()


# Main interface
st.title("Memora – Personal AI")
st.caption("An AI assistant that learns from your conversations.")


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask me anything...")


if question:

    user_id = st.session_state.user_id.strip()

    if not user_id:
        st.warning("Please enter a valid User ID.")
        st.stop()

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Preserve previous history for context
    previous_history = st.session_state.messages.copy()

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    st.session_state.question_count += 1

    try:

        with st.chat_message("assistant"):

            with st.spinner("Thinking and retrieving memories..."):

                answer, memory_updated = chat_service.chat(
    user_id=user_id,
    conversation_id=st.session_state.conversation_id,
    question=question,
    history=previous_history
)
                st.markdown(answer)

                if memory_updated:
                    st.success("🧠 I've learned new preferences from our conversations!")
            

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:

        st.error(f"Chat error: {e}")

        st.session_state.question_count -= 1

        st.session_state.messages.pop()