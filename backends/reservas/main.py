import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base, SCHEMA_NAME, SessionLocal
from sqlalchemy import text
from routers.reservas import router as reservas_router, liberar_espacio_remoto
from models import Reserva, EstadoReserva
from fastapi.middleware.cors import CORSMiddleware
from logger_config import setup_logger

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from time_utils import utc_now

logger = setup_logger("reservas")
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# Tarea en segundo plano para expiracion automatica de reservas pendientes cada 30 segundos
async def background_expirar_reservas():
    while True:
        try:
            await asyncio.sleep(30)
            db = SessionLocal()
            ahora = utc_now()

            # Obtener espacios a liberar de las reservas pendientes vencidas
            vencidas_info = db.query(Reserva.id, Reserva.espacio_id).filter(
                Reserva.estado == EstadoReserva.pendiente,
                Reserva.expira_en != None,
                Reserva.expira_en < ahora
            ).all()

            if vencidas_info:
                # UPDATE atomico de una sola instruccion para evitar carreras con /confirmar
                db.query(Reserva).filter(
                    Reserva.estado == EstadoReserva.pendiente,
                    Reserva.expira_en != None,
                    Reserva.expira_en < ahora
                ).update({"estado": EstadoReserva.cancelada}, synchronize_session=False)
                db.commit()

                for res_id, esp_id in vencidas_info:
                    logger.info("Expirando reserva por tiempo agotado", extra={"reserva_id": res_id, "espacio_id": esp_id})
                    await liberar_espacio_remoto(esp_id)
            db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error en tarea de expiracion", extra={"error": str(e)}, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializacion de esquema y tablas
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # Migracion SQL de columnas y enum
    with engine.connect() as conn:
        conn.execute(text(f"""
            ALTER TABLE {SCHEMA_NAME}.reservas ADD COLUMN IF NOT EXISTS creado_en TIMESTAMP DEFAULT NOW();
            ALTER TABLE {SCHEMA_NAME}.reservas ADD COLUMN IF NOT EXISTS expira_en TIMESTAMP;
            DO $$ BEGIN
                ALTER TYPE {SCHEMA_NAME}.estadoreserva ADD VALUE IF NOT EXISTS 'en_curso';
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
            DO $$ BEGIN
                ALTER TYPE {SCHEMA_NAME}.estadoreserva ADD VALUE IF NOT EXISTS 'fallida';
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
    description="Microservicio independiente para gestion de reservas, exclusion mutua y expiracion automatica.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Internal-Key"],
)

app.include_router(reservas_router)


@app.get("/")
def read_root():
    return {"status": "ok", "service": "reservas"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "reservas"}