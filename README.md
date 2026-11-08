# Memora AI --- Conversational Chatbot with Long-Term Memory

Memora AI is a Streamlit-based chatbot that uses Google Gemini for
response generation, local Sentence Transformers embeddings, and
ChromaDB for persistent conversational memory.

The goal is to let the chatbot learn useful user preferences from
earlier conversations and use relevant memories to personalize responses
in later sessions.

## Features

-   **Gemini-powered chat:** Generates responses using the Google Gemini
    API.
-   **Local embeddings:** Uses `sentence-transformers/all-MiniLM-L6-v2`
    to create 384-dimensional text embeddings locally.
-   **Persistent conversation memory:** Stores question-and-answer
    interactions in ChromaDB.
-   **Semantic retrieval:** Finds relevant earlier interactions using
    vector similarity.
-   **User-specific memory:** Associates stored conversations and
    profiles with a user ID.
-   **Preference extraction:** Uses Gemini to extract structured
    preferences from recent conversations.
-   **Profile persistence:** Stores a user's learned preferences
    separately from raw conversation records.
-   **Memory updates:** Supports active and superseded preference states
    to represent preference changes.
-   **Streamlit interface:** Provides a chat interface and a memory
    dashboard for viewing and managing saved preferences.

> Memory extraction is configured to run after a batch of five new
> interactions. Verify the counter and batch-processing behaviour in
> your local implementation before relying on it in production.

## Technology Stack

  Component                   Technology
  --------------------------- ----------------------------------------------
  User interface              Streamlit
  LLM                         Google Gemini (`google-genai`)
  Embedding model             Sentence Transformers --- `all-MiniLM-L6-v2`
  Vector database             ChromaDB
  Data validation             Pydantic
  Environment configuration   python-dotenv
  Language                    Python

## Architecture

``` text
                         User
                           |
                           v
                     Streamlit UI
                           |
                           v
                     Chat Service
                           |
               +-----------+-----------+
               |                       |
               v                       v
        User Profile Store      Conversation Store
        (semantic memory)       (episodic memory)
               |                       |
               +-----------+-----------+
                           |
                           v
                       Gemini LLM
                           |
                           v
                    Personalized Answer
                           |
                           v
                  Save Question + Answer
                           |
                           v
                   Interaction Counter
                           |
                    Five new interactions?
                           |
                           v
                  Gemini Memory Extractor
                           |
                           v
                Update User Preference Profile
```

### Memory design

Memora separates memory into two categories:

**1. Episodic memory**

Stores conversation interactions, including the user's question, the
assistant's answer, user ID, conversation ID, and timestamp. The
interaction text is embedded and saved in the `conversation_memory`
ChromaDB collection.

**2. Semantic memory**

Stores extracted information about a user, such as likes, dislikes,
interests, and preferences. The profile is saved in the
`user_profile_memory` ChromaDB collection.

Keeping these collections separate allows the application to retrieve
relevant past conversations while also using a compact profile of
learned preferences.

## Project Structure

``` text
chatbot_memory/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
│
├── config/
│   └── settings.py
│
├── core/
│   ├── llm.py
│   ├── embeddings.py
│   └── prompts.py
│
├── memory/
│   ├── conversation_store.py
│   ├── profile_store.py
│   ├── memory_extractor.py
│   ├── memory_retriever.py
│   └── memory_manager.py
│
├── services/
│   ├── chat_service.py
│   ├── context_builder.py
│   └── memory_dashboard.py
│
└── chroma_db/
```

The exact files may vary as the project evolves. The `chroma_db/`
directory is created by ChromaDB when persistent storage is initialized.

## Prerequisites

-   Python 3.10 or newer
-   A Google Gemini API key
-   Internet access for Gemini API requests and the initial
    embedding-model download

## Installation

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd chatbot_memory
```

Replace `<your-repository-url>` with the URL of your repository.

### 2. Create and activate a virtual environment

**Windows:**

``` bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

A basic `requirements.txt` can contain:

``` text
streamlit
chromadb
sentence-transformers
google-genai
python-dotenv
pydantic
```

For reproducible deployments, pin and test the dependency versions used
by your environment.

### 4. Configure environment variables

Create a `.env` file in the project root:

``` env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Use a Gemini model that is available to your API key and supported by
your account.

Do not commit `.env` or expose your API key in source code.

### 5. Run the application

``` bash
streamlit run app.py
```

Streamlit will print a local URL, usually:

``` text
http://localhost:8501
```

Open that address in your browser.

## How to Test Long-Term Memory

Use the same user ID throughout both conversations.

### Conversation 1 --- Teach the chatbot preferences

Send several separate messages, for example:

1.  I love science-fiction movies.
2.  My favourite movie is Interstellar.
3.  I prefer slow-paced movies.
4.  I dislike horror movies.
5.  I enjoy movies about space exploration.

After the configured extraction threshold is reached, inspect the user's
profile in the memory dashboard or directly in ChromaDB.

### Conversation 2 --- Test memory reuse

1.  Start a new conversation.
2.  Keep the same user ID.
3.  Ask: `Suggest some movies for tonight.`

The chatbot should use relevant stored preferences, such as science
fiction, slow pacing, and the user's dislike of horror.

### Additional tests

-   Restart Streamlit and check that stored memories remain available.
-   Use a different user ID and verify that the first user's memories
    are not retrieved.
-   Change a preference and check whether the profile is updated.
-   Delete a preference and verify that it is no longer used.
-   Ask an unrelated question and check that irrelevant memories do not
    affect the answer.

## Data Storage

ChromaDB uses local persistent storage at:

``` text
./chroma_db
```

The application uses two collections:

  -----------------------------------------------------------------------
  Collection                          Purpose
  ----------------------------------- -----------------------------------
  `conversation_memory`               Stores embedded question-and-answer
                                      interactions

  `user_profile_memory`               Stores each user's extracted
                                      preference profile
  -----------------------------------------------------------------------

Back up this directory if you need to preserve local memory data. Do not
share it publicly because it may contain personal conversation
information.

## Privacy and Security Considerations

-   Treat user IDs as identifiers, not as authentication.
-   Add authentication and authorization before exposing the app to
    multiple users.
-   Never expose one user's conversation or profile to another user.
-   Keep API keys in environment variables or a secrets manager.
-   Provide clear controls for viewing and deleting stored user data.
-   Avoid storing sensitive personal information unless there is a clear
    need and appropriate user consent.
-   Review and validate extracted memories; LLM extraction can be
    incorrect.
-   Do not treat retrieved conversation text as trusted system
    instructions.

## Current Scope and Limitations

This is an educational project and a prototype, not a production-ready
multi-tenant service.

-   Memory extraction quality depends on the LLM and the quality of
    conversation context.
-   Semantic similarity does not guarantee that a retrieved memory is
    relevant.
-   Preference changes and contradictions require careful validation.
-   Local ChromaDB storage is not a substitute for production database
    operations, backups, or access control.
-   The embedding model is downloaded locally on first use.
-   The app should be tested for batch-counter correctness, concurrent
    requests, and user isolation before deployment.

## Future Improvements

Potential improvements include:

-   Hybrid retrieval combining semantic similarity and metadata filters.
-   Better memory deduplication and contradiction resolution.
-   Memory confidence and recency scoring.
-   Automated retrieval and extraction evaluation.
-   Conversation export and complete user-data deletion.
-   Authentication and production-grade database deployment.
-   Tests for multiple users, concurrent interactions, and application
    restarts.

## License

Add the license you intend to use before distributing this project.
