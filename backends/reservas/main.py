import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base, SCHEMA_NAME, SessionLocal
from sqlalchemy import text
from routers.reservas import router as reservas_router, liberar_espacio_remoto
from models import Reserva, EstadoReserva
from fastapi.middleware.cors import CORSMiddleware

from time_utils import utc_now

# Tarea en segundo plano para expiración automática de reservas pendientes cada 30 segundos
async def background_expirar_reservas():
    while True:
        try:
            await asyncio.sleep(30)
            db = SessionLocal()
            ahora = utc_now()
            vencidas = db.query(Reserva).filter(
                Reserva.estado == EstadoReserva.pendiente,
                Reserva.expira_en != None,
                Reserva.expira_en < ahora
            ).all()

            for r in vencidas:
                print(f"[RESERVAS BACKGROUND] Expirando reserva #{r.id} por tiempo agotado...")
                r.estado = EstadoReserva.cancelada
                db.commit()
                await liberar_espacio_remoto(r.espacio_id)
            db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[RESERVAS BACKGROUND] Error en tarea de expiración: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de esquema y tablas
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # Migración SQL de columnas y enum
    with engine.connect() as conn:
        conn.execute(text(f"""
            ALTER TABLE {SCHEMA_NAME}.reservas ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP DEFAULT NOW();
            ALTER TABLE {SCHEMA_NAME}.reservas ADD COLUMN IF NOT EXISTS expira_en TIMESTAMP;
            DO $$ BEGIN
                ALTER TYPE {SCHEMA_NAME}.estadoreserva ADD VALUE IF NOT EXISTS 'en_curso';
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """))
        conn.commit()

    task = asyncio.create_task(background_expirar_reservas())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Servicio de Reservas",
    description="Microservicio independiente para gestión de reservas, exclusión mutua y expiración automática.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reservas_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "reservas"}
