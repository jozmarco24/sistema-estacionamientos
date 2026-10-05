from datetime import datetime, timezone, timedelta
from typing import Tuple

LIMA_OFFSET_HOURS = -5
LIMA_TIMEZONE = timezone(timedelta(hours=LIMA_OFFSET_HOURS))

def utc_now() -> datetime:
    """Retorna la fecha y hora actual en UTC (naive para compatibilidad con Postgres sin tz)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def to_utc(dt: datetime) -> datetime:
    """Normaliza cualquier datetime (naive o aware) a UTC naive."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

def to_lima(dt: datetime) -> datetime:
    """Convierte un datetime (UTC o naive asumido UTC) al timezone de Lima (UTC-5)."""
    if dt.tzinfo is None:
        utc_dt = dt.replace(tzinfo=timezone.utc)
    else:
        utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.astimezone(LIMA_TIMEZONE)

def get_hora_lima(dt: datetime) -> int:
    """Extrae la hora (0-23) correspondiente a la zona horaria de Lima (UTC-5)."""
    return to_lima(dt).hour

def es_horario_diurno(dt: datetime, hora_inicio_dia: int = 8, hora_inicio_noche: int = 20) -> bool:
    """Determina si un datetime corresponde al horario diurno en Lima."""
    hora = get_hora_lima(dt)
    return hora_inicio_dia <= hora < hora_inicio_noche
