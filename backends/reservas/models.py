import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Enum, DateTime, String
from database import Base, SCHEMA_NAME

class EstadoReserva(str, enum.Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    en_curso = "en_curso"
    cancelada = "cancelada"
    finalizada = "finalizada"

class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)
    espacio_id = Column(Integer, nullable=False, index=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.pendiente, nullable=False)
    placa_vehiculo = Column(String(20), nullable=False, default="N/A")
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expira_en = Column(DateTime, nullable=True)
