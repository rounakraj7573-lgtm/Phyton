FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/main.py .
ENV PORT=8000
EXPOSE 8000

# IMPORTANT: Docker socket access is powerful. Deploy only on a dedicated
# host, never share it with unrelated workloads, and use a restricted host.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
