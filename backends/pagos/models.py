# backends/pagos/models.py
import enum
from sqlalchemy import Column, Integer, Float, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base, SCHEMA_NAME

class TipoPago(str, enum.Enum):
    suscripcion = "suscripcion"
    reserva = "reserva"

class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    pagado_sin_confirmar = "pagado_sin_confirmar"
    fallido = "fallido"

class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoPago), default=TipoPago.reserva, nullable=False)

    # Origen
    reserva_id = Column(Integer, nullable=True, index=True)
    suscripcion_id = Column(Integer, nullable=True, index=True)
    sede_id = Column(Integer, nullable=True, index=True)

    # Actores
    pagador_id = Column(Integer, nullable=False, index=True)
    receptor_id = Column(Integer, nullable=True, index=True)
    cuenta_destino = Column(String(150), nullable=True)

    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50), nullable=False, default="tarjeta")
    estado = Column(Enum(EstadoPago), default=EstadoPago.pendiente, nullable=False)
    fecha_pago = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Culqi Tracking & Auditoria
    culqi_charge_id = Column(String(100), nullable=True, unique=True, index=True)
    referencia_externa = Column(String(100), nullable=True, index=True)

class CredencialCulqi(Base):
    __tablename__ = "credenciales_culqi"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    propietario_id = Column(Integer, nullable=False, unique=True, index=True)
    public_key_enc = Column(String(500), nullable=True)
    secret_key_enc = Column(String(500), nullable=True)
    esta_verificada = Column(Boolean, default=False, nullable=True)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Columnas previas para retrocompatibilidad
    public_key = Column(String(100), nullable=True)
    secret_key_cifrada = Column(String(500), nullable=True)
    valida = Column(Boolean, default=False, nullable=True)
    verificada_en = Column(DateTime(timezone=True), nullable=True)
