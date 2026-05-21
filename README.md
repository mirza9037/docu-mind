# 🧠 DocuMind: Full-Stack RAG Platform

DocuMind is a production-ready web application that enables users to securely upload documents (such as PDFs and TXTs) and intuitively converse with them to extract precise, context-aware insights.

The application is built on a high-performance FastAPI backend for the web framework, LangChain for orchestration, and ChromaDB for the vector database. When documents are uploaded, they are chunked and embedded locally using HuggingFace's sentence-transformers, with the resulting vectors stored in a persistent, local ChromaDB database—ensuring that sensitive data never leaves the local environment for storage.

During the chat phase, relevant document chunks are retrieved via semantic search and passed as context to a blazing-fast Large Language Model. The system leverages Groq's LPU inference engine, using the llama3-8b-8192 model as the default LLM, to stream responses back to the user almost instantly, complete with accurate citations.

---

## 🚀 Key Features

* **Secure & Local Processing:** Document embeddings are generated and stored entirely locally using sentence-transformers and a persistent ChromaDB instance.
* **Lightning-Fast Inference:** Powered by Groq's LPU for near-instantaneous, cited chat responses.
* **Interactive UI:** A sleek, responsive frontend built with Vanilla HTML, CSS, and JavaScript, featuring modern glassmorphism design and dynamic uploading states.
* **Comprehensive API:** A full set of RESTful API endpoints documented interactively via Swagger UI.
* **One-Click Deployment:** The entire full-stack application is fully containerized with Docker.

---

## 🛠️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Web Framework** | FastAPI |
| **LLM** | Groq (llama3-8b-8192) |
| **Orchestration** | LangChain |
| **Vector Database** | ChromaDB (persistent, local) |
| **Embeddings** | sentence-transformers (local, free) |
| **Deployment** | Docker & Docker Compose |

---

## ⚙️ Quick Start

### Prerequisites

* Python 3.11+
* Docker & Docker Compose (optional, for containerized run)
* A free Groq API Key

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/documind.git
cd documind
```

**2. Set up the environment**
Create a virtual environment and install the required dependencies:

```bash
python -m venv .venv
# Windows: 
.\.venv\Scripts\activate  
# Mac/Linux: 
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Configure environment variables**
Duplicate the example environment file and add your Groq API key:

```bash
cp .env.example .env
```

**4. Run the application**
Start the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/** for the Frontend UI, or **http://localhost:8000/docs** for the interactive Swagger API documentation.

### 🐳 Docker Deployment

To spin up the entire stack seamlessly:

```bash
docker-compose up --build
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| **GET** | `/health` | Liveness check |
| **POST** | `/documents/upload` | Upload a PDF or .txt file |
| **GET** | `/documents/` | List all stored documents |
| **DELETE** | `/documents/{id}` | Delete a specific document |
| **POST** | `/chat/` | Ask a question against an uploaded document |

---

## 👨‍💻 Author

**Mirza Obaid**

* **LinkedIn:** [linkedin.com/in/mirzaobaid](https://www.linkedin.com/in/mirzaobaid)
