from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import CurrentUser, get_current_user
from database import get_db
from models import Incidencia, Sede
from schemas import IncidenciaCreate, IncidenciaResponse

router = APIRouter(
    prefix="/incidencias",
    tags=["Incidencias"]
)

@router.post("/", response_model=IncidenciaResponse)
def crear_incidencia(
    incidencia: IncidenciaCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    sede = db.query(Sede).filter(Sede.id == incidencia.sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada")
    
    fecha_actual = datetime.now().isoformat()
    db_incidencia = Incidencia(
        sede_id=incidencia.sede_id,
        operador_id=current_user.id,
        descripcion=incidencia.descripcion,
        fecha_reporte=fecha_actual
    )
    db.add(db_incidencia)
    db.commit()
    db.refresh(db_incidencia)
    return db_incidencia

@router.get("/sede/{sede_id}", response_model=List[IncidenciaResponse])
def listar_incidencias_por_sede(sede_id: int, db: Session = Depends(get_db)):
    incidencias = db.query(Incidencia).filter(Incidencia.sede_id == sede_id).all()
    return incidencias

@router.get("/", response_model=List[IncidenciaResponse])
def listar_todas_incidencias(db: Session = Depends(get_db)):
    return db.query(Incidencia).order_by(Incidencia.fecha_reporte.desc()).all()

@router.get("/propietario/{propietario_id}", response_model=List[IncidenciaResponse])
def listar_incidencias_por_propietario(propietario_id: int, db: Session = Depends(get_db)):
    sedes_ids = [sede.id for sede in db.query(Sede.id).filter(Sede.propietario_id == propietario_id).all()]
    if not sedes_ids:
        return []
    incidencias = db.query(Incidencia).filter(Incidencia.sede_id.in_(sedes_ids)).all()
    return incidencias

@router.put("/{incidencia_id}/resolver", response_model=IncidenciaResponse)
def resolver_incidencia(
    incidencia_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    from models import EstadoIncidencia
    incidencia = db.query(Incidencia).filter(Incidencia.id == incidencia_id).first()
    if not incidencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidencia no encontrada")
    
    sede = db.query(Sede).filter(Sede.id == incidencia.sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede asociada no encontrada")
        
    if current_user.rol == "operador" and current_user.sede_id != sede.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes resolver incidencias de otra sede")
    elif current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes resolver incidencias de una sede ajena")
    elif current_user.rol not in ["admin", "propietario", "operador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos")
        
    incidencia.estado = EstadoIncidencia.resuelta
    db.commit()
    db.refresh(incidencia)
    return incidencia
