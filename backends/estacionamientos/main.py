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

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Internal-Key"],
)

app.include_router(sedes_router)
app.include_router(espacios_router)
app.include_router(incidencias_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "estacionamientos"}
