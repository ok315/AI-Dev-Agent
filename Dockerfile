FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first, explicitly — avoids pulling the
# full GPU build (several GB), which is useless on a cloud server
# with no GPU anyway.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --break-system-packages

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY src/ ./src/
COPY chroma_db/ ./chroma_db/
EXPOSE 80

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "80"]