# backends/usuarios/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base, SCHEMA_NAME, SessionLocal
from routers.usuarios import router as usuarios_router
from models import Usuario, RolUsuario, Plan
from auth import hash_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # Seeding inicial: Admin Global y Planes
    db = SessionLocal()
    try:
        admin_exists = db.query(Usuario).filter(Usuario.rol == RolUsuario.admin).first()
        if not admin_exists:
            default_admin = Usuario(
                nombre=os.getenv("ADMIN_NOMBRE", "Admin Global"),
                email=os.getenv("ADMIN_EMAIL", "admin@smartpark.com"),
                password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "admin123")),
                rol=RolUsuario.admin,
                activo=True
            )
            db.add(default_admin)
            db.commit()
            print("[USUARIOS] Admin Global creado.")

        planes_count = db.query(Plan).count()
        if planes_count == 0:
            planes_iniciales = [
                Plan(nombre="Basico",      precio=49.00,  max_sedes=1,  max_operadores=2,  activo=True),
                Plan(nombre="Pro",         precio=99.00,  max_sedes=5,  max_operadores=10, activo=True),
                Plan(nombre="Enterprise",  precio=199.00, max_sedes=20, max_operadores=50, activo=True),
            ]
            db.add_all(planes_iniciales)
            db.commit()
            print("[USUARIOS] Planes iniciales creados.")
    except Exception as e:
        print(f"[USUARIOS] Error en seeding: {e}")
    finally:
        db.close()

    yield

app = FastAPI(
    title="Servicio de Usuarios",
    description="Microservicio para gestion de usuarios, login JWT y roles.",
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

app.include_router(usuarios_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "usuarios"}
