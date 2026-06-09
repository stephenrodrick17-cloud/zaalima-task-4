# Architecture
This document explains how zaalima-task-4 is structured at a high level and how a request flows through the system.

## High-level components
- **Frontend**: UI for authentication, chat, and document upload.
- **Backend API**: Handles auth verification, chat requests, document ingestion, and retrieval.
- **Database / Storage**: Stores users, documents, and metadata (project-specific).
- **LLM Provider**: Uses **OpenRouter** for model access.

## Typical request flows
### 1) Sign-in / auth

1. User signs in from the frontend.
2. Frontend obtains a session token from Clerk.
3. Frontend calls backend endpoints with the token.
4. Backend verifies the token using `CLERK_SECRET_KEY`.

### 2) Chat

1. Frontend sends a message to the backend.
2. Backend (optionally) retrieves relevant context from stored documents.
3. Backend calls OpenRouter with `OPENROUTER_API_KEY`.
4. Backend returns the model response to the frontend.

### 3) Document upload + retrieval (RAG)

1. Frontend uploads a document.
2. Backend extracts text (project-specific).
3. Backend creates embeddings (model/provider depends on your code).
4. Backend stores:
   - raw document (or reference)
   - chunks
   - embeddings / vectors (if using a vector DB)
5. During chat, backend runs similarity search and injects retrieved chunks.

## Configuration

- Secrets live in `backend/.env` (never commit).
- See `API_KEYS_NEEDED.md` for required keys.

## Suggested directories (project-specific)

If your repo follows a common layout, it may look like:

- `frontend/` – UI
- `backend/` – API server
- `backend/src/routes` – HTTP endpoints
- `backend/src/services` – OpenRouter / embeddings / RAG services
- `backend/src/db` – DB connection + models

## Observability

Recommended (optional):

- Request logging (pino/winston)
- Structured error responses
- Rate limiting on auth + chat endpoints

