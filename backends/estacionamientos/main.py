# backends/estacionamientos/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base, SCHEMA_NAME
from routers.sedes import router as sedes_router
from routers.espacios import router as espacios_router
from routers.incidencias import router as incidencias_router
from logger_config import setup_logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = setup_logger("estacionamientos")

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # Migracion para asegurar valor 'bloqueado' en enum estadoespacio
    with engine.connect() as conn:
        conn.execute(text(f"""
            DO $$ BEGIN
                ALTER TYPE {SCHEMA_NAME}.estadoespacio ADD VALUE IF NOT EXISTS 'bloqueado';
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """))
        conn.commit()
    yield

app = FastAPI(
    title="Servicio de Estacionamientos",
    description="Microservicio para gestion de sedes, espacios y disponibilidad.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:8081,http://localhost:5173,http://localhost:3000").split(",") if origin.strip()]
if "*" not in ALLOWED_ORIGINS and not os.getenv("ALLOWED_ORIGINS"):
    ALLOWED_ORIGINS.extend(["http://localhost:8081", "http://localhost:8080"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sedes_router)
app.include_router(espacios_router)
app.include_router(incidencias_router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "estacionamientos"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "estacionamientos"}

