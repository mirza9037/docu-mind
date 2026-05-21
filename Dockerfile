FROM python:3.11-slim

WORKDIR /app

# Install system deps for ChromaDB/SQLite and system utilities
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ... (rest of your Dockerfile stays the exact same) ...

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]