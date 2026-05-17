# 🧠 DocuMind API

A production-ready **RAG (Retrieval-Augmented Generation)** backend built with FastAPI, LangChain, ChromaDB, and Groq.

Upload documents → Ask questions → Get cited answers.

---

## Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| LLM | Groq (llama3-8b-8192) |
| Orchestration | LangChain |
| Vector DB | ChromaDB (persistent, local) |
| Embeddings | sentence-transformers (local, free) |
| Testing | pytest + httpx |

---

## Quick Start

```bash
# 1. Clone and enter project
git clone https://github.com/yourusername/documind-api
cd documind-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at console.groq.com)

# 5. Run the API
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/documents/upload` | Upload a PDF or .txt file |
| GET | `/documents/` | List all stored documents |
| DELETE | `/documents/{id}` | Delete a document |
| POST | `/chat/` | Ask a question |

---

## Example Usage

**Upload a document:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@my_report.pdf"
```

**Chat with it:**
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "document_id": "your-doc-id-here"
  }'
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Docker

```bash
docker-compose up --build
```
