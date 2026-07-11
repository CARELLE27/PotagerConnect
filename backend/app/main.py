import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.routers import auth, cultures, parcelles

logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)

app = FastAPI(
    title="PotagerConnect API",
    description="Gestion de jardins partages communautaires - Projet 3PRJ3",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose /metrics pour Prometheus (requetes/sec, latence, codes HTTP).
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.include_router(auth.router)
app.include_router(parcelles.router)
app.include_router(parcelles.users_router)
app.include_router(cultures.router)


@app.get("/health", tags=["monitoring"])
def health():
    """Sonde de liveness, utilisee par Docker et par l'alerte 'service down'."""
    return {"status": "ok"}
