import os
import math
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Sede
from schemas import SedeCreate, SedeResponse, SedeCercanaResponse, SedeEstadoUpdate
from auth import (
    get_current_user, require_admin, require_propietario,
    CurrentUser
)

router = APIRouter(prefix="/sedes", tags=["sedes"])

USUARIOS_SERVICE_URL = os.getenv("USUARIOS_SERVICE_URL", "http://usuarios:8001")
PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://pagos:8004")
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
        
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

@router.post("/", response_model=SedeResponse, status_code=status.HTTP_201_CREATED)
async def crear_sede(
    sede_in: SedeCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    propietario_id = current_user.id if current_user.rol == "propietario" else sede_in.propietario_id

    # Validar límite de SaaS en servicio usuarios con X-Internal-Key
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            r = await client.get(
                f"{USUARIOS_SERVICE_URL}/usuarios/suscripcion/limites/{propietario_id}",
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
            if r.status_code != 200:
                raise HTTPException(status_code=403, detail="Propietario no tiene suscripción activa o superó su plan.")
            limites = r.json()
            sedes_actuales = db.query(Sede).filter(Sede.propietario_id == propietario_id).count()
            if sedes_actuales >= limites.get("max_sedes", 1):
                raise HTTPException(status_code=403, detail=f"Límite de sedes alcanzado ({limites.get('max_sedes')}) para el plan actual.")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error de conexión con servicio de usuarios")

    data = sede_in.model_dump()
    data["propietario_id"] = propietario_id
    nueva_sede = Sede(**data, activa=True)
    db.add(nueva_sede)
    db.commit()
    db.refresh(nueva_sede)
    return nueva_sede

@router.get("/", response_model=List[SedeResponse])
def listar_sedes(db: Session = Depends(get_db)):
    return db.query(Sede).all()

@router.get("/cercanas", response_model=List[SedeCercanaResponse])
async def listar_sedes_cercanas(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    db: Session = Depends(get_db)
):
    lat_val = lat if lat is not None else latitud
    lon_val = lon if lon is not None else longitud
    if lat_val is None or lon_val is None:
        raise HTTPException(status_code=400, detail="Debe proporcionar latitud y longitud.")
    sedes = db.query(Sede).filter(Sede.activa == True).all()
    
    # Consultar qué propietarios tienen credenciales Culqi válidas
    propietarios_ids = list(set([s.propietario_id for s in sedes]))
    propietarios_validos = set()
    
    async with httpx.AsyncClient(timeout=6.0) as client:
        for pid in propietarios_ids:
            try:
                res_culqi = await client.get(
                    f"{PAGOS_SERVICE_URL}/pagos/internal/propietario/{pid}/culqi-valida",
                    headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
                )
                if res_culqi.status_code == 200 and res_culqi.json().get("valida", False):
                    propietarios_validos.add(pid)
            except Exception as e:
                print(f"Error consultando culqi para propietario {pid}: {e}")

    sedes_con_distancia = []
    for s in sedes:
        dist = calcular_distancia_haversine(lat_val, lon_val, s.latitud, s.longitud)
        sedes_con_distancia.append({
            "id": s.id,
            "nombre": s.nombre,
            "direccion": s.direccion,
            "latitud": s.latitud,
            "longitud": s.longitud,
            "propietario_id": s.propietario_id,
            "activa": s.activa,
            "tarifa_hora": s.tarifa_hora,
            "tarifa_auto_dia": s.tarifa_auto_dia,
            "tarifa_auto_noche": s.tarifa_auto_noche,
            "tarifa_moto_dia": s.tarifa_moto_dia,
            "tarifa_moto_noche": s.tarifa_moto_noche,
            "distancia_km": round(dist, 2),
            "culqi_activo": (s.propietario_id in propietarios_validos)
        })
        
    sedes_con_distancia.sort(key=lambda x: x["distancia_km"])
    return sedes_con_distancia

@router.get("/propietario/{propietario_id}", response_model=List[SedeResponse])
def listar_sedes_por_propietario(
    propietario_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.rol != "admin" and (current_user.rol != "propietario" or current_user.id != propietario_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las sedes de otro propietario")
    return db.query(Sede).filter(Sede.propietario_id == propietario_id).all()

@router.get("/{sede_id}", response_model=SedeResponse)
def obtener_sede(sede_id: int, db: Session = Depends(get_db)):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    return sede

@router.put("/{sede_id}/estado", response_model=SedeResponse)
def actualizar_estado_sede(
    sede_id: int,
    estado_in: SedeEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    if current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes alterar una sede que no te pertenece")
    
    sede.activa = estado_in.activa
    db.commit()
    db.refresh(sede)
    return sede

@router.put("/{sede_id}", response_model=SedeResponse)
def actualizar_sede(
    sede_id: int,
    sede_in: SedeCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    
    if current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes modificar una sede ajena")

    sede.nombre = sede_in.nombre
    sede.direccion = sede_in.direccion
    sede.latitud = sede_in.latitud
    sede.longitud = sede_in.longitud
    sede.tarifa_hora = sede_in.tarifa_hora
    sede.tarifa_auto_dia = sede_in.tarifa_auto_dia if sede_in.tarifa_auto_dia is not None else sede.tarifa_auto_dia
    sede.tarifa_auto_noche = sede_in.tarifa_auto_noche if sede_in.tarifa_auto_noche is not None else sede.tarifa_auto_noche
    sede.tarifa_moto_dia = sede_in.tarifa_moto_dia if sede_in.tarifa_moto_dia is not None else sede.tarifa_moto_dia
    sede.tarifa_moto_noche = sede_in.tarifa_moto_noche if sede_in.tarifa_moto_noche is not None else sede.tarifa_moto_noche
    sede.hora_inicio_dia = sede_in.hora_inicio_dia if sede_in.hora_inicio_dia is not None else sede.hora_inicio_dia
    sede.hora_inicio_noche = sede_in.hora_inicio_noche if sede_in.hora_inicio_noche is not None else sede.hora_inicio_noche
    
    db.commit()
    db.refresh(sede)
    return sede

@router.delete("/{sede_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    if current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar una sede ajena")
    
    db.delete(sede)
    db.commit()
    return None
