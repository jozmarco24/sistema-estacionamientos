
from fastapi import FastAPI
from database import engine, Base, SCHEMA_NAME
from sqlalchemy import text
from routers.sedes import router as sedes_router
from routers.espacios import router as espacios_router
from routers.incidencias import router as incidencias_router

# Autocrea el esquema y las tablas en el esquema correspondiente
with engine.connect() as conn:
    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
    conn.commit()

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Servicio de Estacionamientos",
    description="Microservicio independiente para gestión de sedes, espacios y disponibilidad.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sedes_router)
app.include_router(espacios_router)
app.include_router(incidencias_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "estacionamientos"}
