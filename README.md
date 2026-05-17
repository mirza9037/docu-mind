# 🧠 DocuMind

A full-stack, production-ready **Retrieval-Augmented Generation (RAG)** application. DocuMind allows users to upload documents (PDFs, TXTs) and securely chat with them to extract insights, powered by blazing-fast LLMs and a sleek UI.

Upload documents → Ask questions → Get precise, context-aware answers.

---

## ✨ Features

- **End-to-End Application**: Comes with a fully functional FastAPI backend and a sleek, modern vanilla HTML/JS/CSS frontend.
- **Retrieval-Augmented Generation (RAG)**: Leverages your own documents as context to answer complex queries accurately.
- **Blazing Fast LLM**: Powered by Groq's LPU inference engine for near-instant response times.
- **Local Vector Database**: Uses ChromaDB for fast, persistent, and local document embedding retrieval.
- **RESTful API**: Comprehensive API endpoints with Swagger UI documentation out-of-the-box.
- **Docker Ready**: Fully containerized setup for easy deployments using Docker Compose.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Orchestration**: [LangChain](https://python.langchain.com/)
- **LLM Provider**: [Groq](https://console.groq.com/) (llama3-8b-8192)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) (Persistent & Local)
- **Embeddings**: `sentence-transformers` (HuggingFace)

### Frontend
- **Structure**: Vanilla HTML5
- **Styling**: Vanilla CSS (Responsive, Glassmorphism design)
- **Logic**: Vanilla JavaScript (Fetch API for integration)

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/documind.git
cd documind
```

### 3. Set Up Virtual Environment
```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
*Open the `.env` file and insert your `GROQ_API_KEY` (Get one for free at [console.groq.com](https://console.groq.com/keys)).*

### 6. Run the Application
Start the FastAPI server (which also serves the frontend):
```bash
uvicorn app.main:app --reload
```

- **Frontend UI**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker Deployment

Don't want to install dependencies locally? You can run the entire stack using Docker!

```bash
# Build and run the containers
docker-compose up --build
```
The application will be accessible at `http://localhost:8000`.

---

## 📡 API Endpoints

Once the application is running, you can access the interactive Swagger documentation at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/documents/upload` | Upload a PDF or .txt file into the vector database |
| `GET` | `/documents/` | List all stored documents in the system |
| `DELETE` | `/documents/{id}` | Delete a specific document by its ID |
| `POST` | `/chat/` | Ask a question against the uploaded documents |

---

## 📂 Project Structure

```text
documind/
├── app/                      # Backend FastAPI Application
│   ├── api/                  # API Routers and Dependencies
│   ├── core/                 # App config, settings, and logging
│   ├── models/               # Pydantic schemas for request/response
│   ├── services/             # Core business logic (RAG, Vectorstore, Ingestor)
│   └── main.py               # FastAPI entry point
├── frontend/                 # Vanilla Frontend UI assets
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/                     # Local ChromaDB persistent storage (auto-generated)
├── tests/                    # Pytest test suite
├── .env.example              # Environment variable template
├── Dockerfile                # Docker configuration for the API
├── docker-compose.yml        # Docker Compose configuration
└── requirements.txt          # Python dependencies
```

---

## 🧪 Running Tests

To ensure everything is working correctly, you can run the test suite using `pytest`:

```bash
pytest tests/ -v
```

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/documind/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
