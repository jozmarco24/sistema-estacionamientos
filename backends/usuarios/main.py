from fastapi import FastAPI
from database import engine, Base, SCHEMA_NAME
from sqlalchemy import text
from routers.usuarios import router as usuarios_router

# Autocrea el esquema y las tablas en el esquema correspondiente
with engine.connect() as conn:
    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
    conn.commit()

Base.metadata.create_all(bind=engine)

# Semilla: Administrador por defecto y Planes SaaS
from database import SessionLocal
from models import Usuario, RolUsuario, Plan
from auth import hash_password

db = SessionLocal()
try:
    admin_exists = db.query(Usuario).filter(Usuario.rol == RolUsuario.admin).first()
    if not admin_exists:
        default_admin = Usuario(
            nombre="Admin Global",
            email="admin@smartpark.com",
            password_hash=hash_password("admin123"),
            rol=RolUsuario.admin,
            activo=True
        )
        db.add(default_admin)
        db.commit()

    planes_count = db.query(Plan).count()
    if planes_count == 0:
        planes_iniciales = [
            Plan(nombre="Básico", precio=49.00, max_sedes=1, max_operadores=2, activo=True),
            Plan(nombre="Pro", precio=99.00, max_sedes=5, max_operadores=10, activo=True),
            Plan(nombre="Enterprise", precio=199.00, max_sedes=20, max_operadores=50, activo=True)
        ]
        db.add_all(planes_iniciales)
        db.commit()
except Exception as e:
    print(f"Error seeding initial data: {e}")
finally:
    db.close()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Servicio de Usuarios",
    description="Microservicio independiente para gestión de usuarios, login JWT y roles.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "usuarios"}
