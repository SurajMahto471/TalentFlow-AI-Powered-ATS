FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Lean API deps only (no Streamlit) — fits Render free-tier builds better
COPY requirements-api.txt requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl gfortran libopenblas-dev liblapack-dev pkg-config && \
    python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    apt-get purge -y --auto-remove build-essential gfortran pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

# Render injects $PORT — must listen on that port, not hardcoded 8000
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
