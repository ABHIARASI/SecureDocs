# SecureDocs — AI-Powered Document Search Platform

SecureDocs is a full-stack document search platform that lets users upload PDF documents and ask questions about their contents using AI-powered semantic search and Retrieval-Augmented Generation (RAG).

## Features

- **User Authentication:** Secure registration and login using password hashing and JWT authentication.
- **PDF Upload:** Upload and manage PDF documents with file validation.
- **Document Processing:** Extract text from PDFs and split it into smaller chunks for retrieval.
- **Semantic Search:** Generate text embeddings and retrieve relevant document chunks using PostgreSQL and pgvector.
- **AI-Powered Answers:** Generate answers using retrieved document context with the Gemini API.
- **Source References:** Display relevant document excerpts alongside generated answers.
- **Document Management:** View and delete uploaded documents.
- **User Isolation:** Restrict access to documents according to the authenticated user.

## Tech Stack

**Frontend:** React, JavaScript, CSS

**Backend:** Python, FastAPI

**Database:** PostgreSQL, pgvector

**AI and Retrieval:** Sentence Transformers, vector similarity search, Retrieval-Augmented Generation (RAG), Gemini API

**Authentication:** JWT, password hashing

**Tools:** Git, GitHub, Docker (if configured in the current project)

## How It Works

1. A user registers or logs in.
2. The user uploads a PDF document.
3. The backend extracts and chunks the document text.
4. Text embeddings are generated and stored for semantic retrieval.
5. When the user asks a question, SecureDocs retrieves relevant document chunks.
6. The retrieved context is passed to the AI model to generate an answer.
7. The answer and relevant source excerpts are displayed in the frontend.

## Running Locally

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL
- A Gemini API key

### Backend Setup

1. Open a terminal in the backend directory.
2. Create and activate a Python virtual environment.
3. Install the dependencies listed in the project's requirements file.
4. Configure the required environment variables.
5. Start the FastAPI development server.

```bash
uvicorn main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs` when the backend is running with the default configuration.

### Frontend Setup

1. Open a separate terminal in the frontend directory.
2. Install the dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite in the terminal.

## Environment Variables

Configure the required environment variables locally. The exact names should match those used by the application.

Typical examples include:

- `DATABASE_URL`
- `SECRET_KEY`
- `GEMINI_API_KEY`

**Security:** Never commit real API keys, database passwords, JWT secrets, or other credentials to GitHub. Keep `.env` out of version control and provide placeholder values in an `.env.example` file if needed.

## Testing

The backend includes automated tests covering:

- User registration and authentication
- User-level document access isolation
- PDF upload validation
- Document deletion

Run the backend tests from the `backend` directory using:

```bash
pytest
```

## Future Improvements

- Add continuous integration (CI) to run tests automatically on every push.
- Introduce deployment workflows.
- Expand retrieval-quality evaluation and testing.
- Add support for additional document formats.

Developed as a full-stack project exploring secure document management, semantic search, and Retrieval-Augmented Generation.
