# backends/pagos/main.py
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base, SCHEMA_NAME
from routers.pagos import router as pagos_router
from routers.credenciales import router as credenciales_router

# Validacion estricta: Solo modo prueba Culqi
CULQI_SECRET = os.getenv("CULQI_SECRET_KEY", "")
if not CULQI_SECRET.startswith("sk_test_"):
    print("FATAL: CULQI_SECRET_KEY debe iniciar con 'sk_test_'. Modo live no permitido.")
    sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        conn.execute(text(f"""
            ALTER TABLE {SCHEMA_NAME}.pagos ADD COLUMN IF NOT EXISTS culqi_charge_id VARCHAR(100);
            ALTER TABLE {SCHEMA_NAME}.pagos ADD COLUMN IF NOT EXISTS referencia_externa VARCHAR(100);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_pagos_culqi_charge ON {SCHEMA_NAME}.pagos(culqi_charge_id);

            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ADD COLUMN IF NOT EXISTS public_key_enc TEXT;
            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ADD COLUMN IF NOT EXISTS secret_key_enc TEXT;
            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ADD COLUMN IF NOT EXISTS esta_verificada BOOLEAN DEFAULT FALSE;
            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ DEFAULT NOW();
            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ALTER COLUMN public_key DROP NOT NULL;
            ALTER TABLE {SCHEMA_NAME}.credenciales_culqi ALTER COLUMN secret_key_cifrada DROP NOT NULL;
        """))
        conn.commit()
    yield

app = FastAPI(
    title="Servicio de Pagos",
    description="Microservicio para procesamiento de cobros con Culqi (Modo Prueba) y suscripciones SaaS.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:8080")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pagos_router)
app.include_router(credenciales_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "pagos", "modo": "prueba_culqi"}
