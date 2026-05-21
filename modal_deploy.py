"""
modal_deploy.py — Deploy DocuMind API to Modal

Usage:
  1. pip install modal
  2. modal setup              (authenticate once)
  3. modal secret create documind-secrets GROQ_API_KEY=gsk_...
  4. modal deploy modal_deploy.py   (live deployment)
     modal serve modal_deploy.py    (dev mode with hot reload)

Endpoints will be available at the URL Modal prints after deploy.
"""

import modal

# ── Image ──────────────────────────────────────────────────────────────────

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("build-essential", "curl")
    .pip_install_from_requirements("requirements.txt")
    # Pre-download the embedding model at build time → faster cold starts
    .run_commands(
        "python -c \"from sentence_transformers import SentenceTransformer; "
        "SentenceTransformer('all-MiniLM-L6-v2')\""
    )
    # Add project files — exclude heavy/unnecessary directories
    .add_local_dir(
        ".",
        remote_path="/root/documind",
        copy=False,
        ignore=[
            ".venv",
            "venv",
            ".git",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "data",           # ChromaDB lives in the Modal Volume, not here
            "*.egg-info",
            ".pytest_cache",
            "node_modules",
        ],
    )
)

# ── Persistent Volume ──────────────────────────────────────────────────────

chroma_volume = modal.Volume.from_name("documind-chroma-db", create_if_missing=True)
CHROMA_MOUNT_PATH = "/app/data"

# ── App ────────────────────────────────────────────────────────────────────

app = modal.App(
    name="documind-api",
    image=image,
    secrets=[modal.Secret.from_name("documind-secrets")],
)

# ── ASGI entrypoint ────────────────────────────────────────────────────────

@app.function(
    volumes={CHROMA_MOUNT_PATH: chroma_volume},
    min_containers=1,
    timeout=120,
)
@modal.concurrent(max_inputs=10)
@modal.asgi_app()
def fastapi_app():
    import os
    import sys

    if "/root/documind" not in sys.path:
        sys.path.insert(0, "/root/documind")

    os.environ.setdefault("CHROMA_PERSIST_DIR", f"{CHROMA_MOUNT_PATH}/chroma_db")

    from app.main import app as fastapi_application
    return fastapi_application


# ── One-off ingestion helper ───────────────────────────────────────────────

@app.function(
    volumes={CHROMA_MOUNT_PATH: chroma_volume},
    timeout=300,
)
def ingest_sample(file_path: str = "sample_document.txt"):
    """
    Ingest a local file into the deployed ChromaDB volume.
    Example: modal run modal_deploy.py::ingest_sample --file-path my_doc.pdf
    """
    import os
    import sys
    import io
    from pathlib import Path

    if "/root/documind" not in sys.path:
        sys.path.insert(0, "/root/documind")

    os.environ.setdefault("CHROMA_PERSIST_DIR", f"{CHROMA_MOUNT_PATH}/chroma_db")

    from app.services.ingestor import ingest_file
    from fastapi import UploadFile

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    content_type = "application/pdf" if path.suffix == ".pdf" else "text/plain"
    with open(path, "rb") as f:
        data = f.read()

    upload = UploadFile(filename=path.name, file=io.BytesIO(data))
    upload.content_type = content_type

    doc_id, filename, chunks = ingest_file(upload)
    chroma_volume.commit()
    print(f"Ingested '{filename}' → {chunks} chunks (id={doc_id})")