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
from logger_config import setup_logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = setup_logger("usuarios")

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

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
            admin_pwd = os.getenv("ADMIN_PASSWORD")
            if not admin_pwd:
                raise RuntimeError("ADMIN_PASSWORD no está definida en las variables de entorno.")
            default_admin = Usuario(
                nombre=os.getenv("ADMIN_NOMBRE", "Admin Global"),
                email=os.getenv("ADMIN_EMAIL", "admin@smartpark.com"),
                password_hash=hash_password(admin_pwd),
                rol=RolUsuario.admin,
                activo=True
            )
            db.add(default_admin)
            db.commit()
            logger.info("Admin Global creado exitosamente.")

        planes_count = db.query(Plan).count()
        if planes_count == 0:
            planes_iniciales = [
                Plan(nombre="Basico",      precio=49.00,  max_sedes=1,  max_operadores=2,  activo=True),
                Plan(nombre="Pro",         precio=99.00,  max_sedes=5,  max_operadores=10, activo=True),
                Plan(nombre="Enterprise",  precio=199.00, max_sedes=20, max_operadores=50, activo=True),
            ]
            db.add_all(planes_iniciales)
            db.commit()
            logger.info("Planes iniciales creados exitosamente.")
    except Exception as e:
        logger.error("Error en seeding", extra={"error": str(e)}, exc_info=True)
    finally:
        db.close()

    yield

app = FastAPI(
    title="Servicio de Usuarios",
    description="Microservicio para gestion de usuarios, login JWT y roles.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8081").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Internal-Key"],
)

app.include_router(usuarios_router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "usuarios"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "usuarios"}
