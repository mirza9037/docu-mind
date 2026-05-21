# 🧠 DocuMind — AI Document Chat Platform

> Upload documents. Ask questions. Get cited answers — instantly.

DocuMind is a full-stack **Retrieval-Augmented Generation (RAG)** platform. Upload PDFs or text files, and chat with them in natural language. The AI only answers from your documents and always cites its sources.

**Live Demo:**
- 🌐 **Frontend:** [Deployed on Vercel](https://docu-mind-mirza9037.vercel.app)
- ⚡ **Backend API:** [https://mirza9037--documind-api-fastapi-app.modal.run](https://mirza9037--documind-api-fastapi-app.modal.run)
- 📖 **Swagger Docs:** [https://mirza9037--documind-api-fastapi-app.modal.run/docs](https://mirza9037--documind-api-fastapi-app.modal.run/docs)

---

## 🚀 Key Features

- **Local Embeddings** — Documents are chunked and embedded using HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`). No third-party embedding API. Your data stays private.
- **Lightning-Fast LLM** — Powered by Groq's LPU inference engine running `llama-3.1-8b-instant` for near-instant responses.
- **Persistent Vector Store** — ChromaDB stores embeddings in a Modal Volume, surviving restarts and redeployments.
- **Cited Answers** — Every AI response includes the source chunks it was derived from (filename + page number).
- **Multi-turn Chat** — Pass `history[]` in your API calls for context-aware follow-up questions.
- **Scoped Queries** — Optionally pass a `document_id` to restrict retrieval to one specific document.
- **Premium UI** — Glassmorphism dark-mode design with animated orb backgrounds, smooth transitions, and full responsiveness.
- **Production Deployed** — Backend on Modal (serverless, always-on), Frontend on Vercel (CDN-hosted static).

---

## 🛠️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Web Framework** | FastAPI |
| **LLM** | Groq (`llama-3.1-8b-instant`) |
| **Orchestration** | LangChain |
| **Vector Database** | ChromaDB (persistent, Modal Volume) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local, free) |
| **Backend Hosting** | Modal (serverless ASGI) |
| **Frontend Hosting** | Vercel (static CDN) |
| **Containerization** | Docker + Docker Compose (local dev) |

---

## 📁 Project Structure

```
documind/
├── app/                        # FastAPI backend
│   ├── main.py                 # App entrypoint: routers, CORS, lifespan
│   ├── api/
│   │   ├── deps.py             # Shared FastAPI dependencies
│   │   └── routes/
│   │       ├── health.py       # GET /health — liveness + ChromaDB status
│   │       ├── documents.py    # POST /documents/upload, GET, DELETE
│   │       └── chat.py         # POST /chat — RAG question answering
│   ├── core/
│   │   ├── config.py           # Pydantic settings (reads from .env)
│   │   └── logging.py          # Structured logger
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response schemas
│   └── services/
│       ├── ingestor.py         # File parsing, chunking, metadata tagging
│       ├── vectorstore.py      # ChromaDB CRUD (add, search, list, delete)
│       └── rag.py              # RAG pipeline: retrieve → prompt → Groq → cite
├── frontend/                   # Static frontend (deployed to Vercel)
│   ├── index.html              # App shell
│   ├── style.css               # Full glassmorphism design system
│   └── app.js                  # All UI logic, API calls, chat/upload state
├── tests/                      # Pytest test suite
│   ├── conftest.py             # Shared fixtures (TestClient, mocks)
│   ├── test_documents.py       # Upload, list, delete endpoint tests
│   └── test_chat.py            # Chat endpoint + RAG pipeline tests
├── modal_deploy.py             # Modal serverless deployment config
├── vercel.json                 # Vercel static site config (points to frontend/)
├── Dockerfile                  # Docker image (local / self-hosted)
├── docker-compose.yml          # One-command local stack
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (not committed)
```

---

## ⚙️ Local Development

### Prerequisites

- Python 3.11+
- A free [Groq API Key](https://console.groq.com)

### Setup

```bash
# 1. Clone
git clone https://github.com/mirza9037/docu-mind.git
cd docu-mind

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Edit .env and set your GROQ_API_KEY
```

### Environment Variables (`.env`)

```env
# LLM
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Vector Store
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION=documind

# Embeddings (local, no API key)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# App
APP_NAME=DocuMind API
APP_VERSION=1.0.0
MAX_UPLOAD_SIZE_MB=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K_RESULTS=4
```

### Run

```bash
uvicorn app.main:app --reload
```

| URL | Description |
| --- | --- |
| http://localhost:8000/ | Frontend UI |
| http://localhost:8000/docs | Interactive Swagger API docs |
| http://localhost:8000/health | Health check |

---

## 🐳 Docker (Self-Hosted)

```bash
docker-compose up --build
```

The compose file mounts `./data` for ChromaDB persistence and exposes port `8000`.

---

## ☁️ Production Deployment

### Backend → Modal

```bash
# 1. Install Modal
pip install modal

# 2. Authenticate (one-time)
modal setup

# 3. Create secrets
modal secret create documind-secrets GROQ_API_KEY=gsk_...

# 4. Deploy (persistent, always-on)
modal deploy modal_deploy.py

# Dev mode (hot reload, stops on Ctrl+C)
modal serve modal_deploy.py
```

The Modal deploy:
- Builds a Debian Slim image with all Python deps
- Pre-downloads the `all-MiniLM-L6-v2` embedding model at build time (faster cold starts)
- Mounts a persistent `documind-chroma-db` Volume at `/app/data`
- Runs with `min_containers=1` and handles up to 10 concurrent requests

### Frontend → Vercel

The `vercel.json` at the root tells Vercel to serve the `frontend/` directory as a static site:

```json
{
  "outputDirectory": "frontend",
  "buildCommand": "",
  "installCommand": "",
  "framework": null
}
```

Push to `main` → Vercel auto-deploys. Or deploy manually:

```bash
npx vercel --prod
```

---

## 🔌 API Reference

### `GET /health`
Returns liveness status and ChromaDB connection info.

```json
{
  "status": "ok",
  "app": "DocuMind API",
  "version": "1.0.0",
  "vector_store": "connected (42 chunks loaded)"
}
```

### `POST /documents/upload`
Upload a `.pdf` or `.txt` file. Returns a `document_id` for scoped queries.

```bash
curl -X POST https://mirza9037--documind-api-fastapi-app.modal.run/documents/upload \
  -F "file=@my_doc.pdf"
```

```json
{
  "document_id": "uuid-here",
  "filename": "my_doc.pdf",
  "chunk_count": 24,
  "message": "Successfully ingested 'my_doc.pdf' into 24 chunks."
}
```

### `GET /documents/`
List all stored documents with metadata.

```json
{
  "total": 2,
  "documents": [
    {
      "document_id": "uuid",
      "filename": "my_doc.pdf",
      "uploaded_at": "2026-05-21T15:00:00+00:00",
      "chunk_count": 24
    }
  ]
}
```

### `DELETE /documents/{document_id}`
Permanently remove a document and all its chunks from ChromaDB.

### `POST /chat/`
Ask a question. Optionally scope to a document and pass conversation history.

```json
// Request
{
  "question": "What is the refund policy?",
  "document_id": "uuid-here",
  "history": []
}

// Response
{
  "answer": "The refund policy states...",
  "sources": [
    {
      "document_id": "uuid",
      "filename": "my_doc.pdf",
      "excerpt": "Refunds are processed within 7 business days...",
      "page": 3
    }
  ],
  "model_used": "llama-3.1-8b-instant"
}
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Tests use `FastAPI.TestClient` with mocked ChromaDB and Groq LLM — no real API calls or database needed.

---

## 👨‍💻 Author

**Mirza Obaid**

- **LinkedIn:** [linkedin.com/in/mirzaobaid](https://www.linkedin.com/in/mirzaobaid)
- **GitHub:** [github.com/mirza9037](https://github.com/mirza9037)
