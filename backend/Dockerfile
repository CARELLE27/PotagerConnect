# Multi-stage : image finale legere, sans outils de build (bonne pratique 2DCK1/3DCK2)
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root : exigence de securite
RUN useradd -m -u 1000 potager
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=potager:potager app ./app

USER potager
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
