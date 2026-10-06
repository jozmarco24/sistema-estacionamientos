from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Espacio, EstadoEspacio, Sede, TipoVehiculo
from schemas import EspacioCreate, EspacioResponse, ActualizarEstadoEspacio, EspacioLoteCreate
from auth import require_admin, require_propietario, require_operador, get_current_user, CurrentUser, verify_internal_key

router = APIRouter(prefix="/espacios", tags=["espacios"])

@router.post("/", response_model=EspacioResponse, status_code=status.HTTP_201_CREATED)
def crear_espacio(espacio_in: EspacioCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_propietario)):
    sede = db.query(Sede).filter(Sede.id == espacio_in.sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no existe")
        
    if current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes crear espacios en una sede que no te pertenece.")
    
    tipo_v = espacio_in.tipo_vehiculo or TipoVehiculo.auto
    nuevo_espacio = Espacio(
        sede_id=espacio_in.sede_id,
        numero=espacio_in.numero,
        tipo_vehiculo=tipo_v,
        estado=espacio_in.estado or EstadoEspacio.libre
    )
    db.add(nuevo_espacio)
    db.commit()
    db.refresh(nuevo_espacio)
    return nuevo_espacio

@router.get("/", response_model=List[EspacioResponse])
def listar_todos_los_espacios(db: Session = Depends(get_db)):
    return db.query(Espacio).all()

@router.get("/sede/{sede_id}", response_model=List[EspacioResponse])
def listar_espacios_por_sede(sede_id: int, db: Session = Depends(get_db)):
    # Público para conductores que buscan espacio
    return db.query(Espacio).filter(Espacio.sede_id == sede_id).all()

@router.get("/{espacio_id}")
def obtener_espacio_detalle(espacio_id: int, db: Session = Depends(get_db)):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    sede = db.query(Sede).filter(Sede.id == espacio.sede_id).first()
    return {
        "id": espacio.id,
        "sede_id": espacio.sede_id,
        "numero": espacio.numero,
        "tipo_vehiculo": espacio.tipo_vehiculo.value if hasattr(espacio.tipo_vehiculo, "value") else str(espacio.tipo_vehiculo),
        "estado": espacio.estado.value,
        "propietario_id": sede.propietario_id if sede else None,
        "sede_nombre": sede.nombre if sede else "Sede",
        "tarifa_hora": sede.tarifa_hora if sede else 5.0,
        "tarifa_auto_dia": getattr(sede, "tarifa_auto_dia", 6.0),
        "tarifa_auto_noche": getattr(sede, "tarifa_auto_noche", 4.0),
        "tarifa_moto_dia": getattr(sede, "tarifa_moto_dia", 3.0),
        "tarifa_moto_noche": getattr(sede, "tarifa_moto_noche", 2.0),
        "hora_inicio_dia": getattr(sede, "hora_inicio_dia", 8),
        "hora_inicio_noche": getattr(sede, "hora_inicio_noche", 20)
    }

@router.get("/{espacio_id}/disponibilidad")
def consultar_disponibilidad(espacio_id: int, db: Session = Depends(get_db)):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    return {
        "espacio_id": espacio.id,
        "numero": espacio.numero,
        "estado": espacio.estado.value,
        "disponible": espacio.estado == EstadoEspacio.libre
    }

@router.put("/{espacio_id}/estado", response_model=EspacioResponse)
def actualizar_estado(espacio_id: int, payload: ActualizarEstadoEspacio, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_operador)):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
        
    # Verificar aislamiento por sede
    if current_user.rol == "operador" and espacio.sede_id != current_user.sede_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: Este espacio pertenece a otra sede.")
    
    # Verificar aislamiento por propiedad si es propietario
    if current_user.rol == "propietario":
        sede = db.query(Sede).filter(Sede.id == espacio.sede_id).first()
        if sede.propietario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: Esta sede no te pertenece.")
            
    espacio.estado = payload.estado
    db.commit()
    db.refresh(espacio)
    return espacio

@router.put("/{espacio_id}/reservar_atomico", response_model=EspacioResponse)
def reservar_espacio_atomico(espacio_id: int, db: Session = Depends(get_db), _internal: bool = Depends(verify_internal_key)):
    # Consumido internamente por el microservicio de reservas: soft-lock / bloqueo temporal
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).with_for_update().first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    
    if espacio.estado != EstadoEspacio.libre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El espacio {espacio.numero} no está disponible (estado actual: {espacio.estado.value})"
        )
    
    espacio.estado = EstadoEspacio.bloqueado
    db.commit()
    db.refresh(espacio)
    return espacio

@router.put("/{espacio_id}/reservar", response_model=EspacioResponse)
def marcar_espacio_reservado(espacio_id: int, db: Session = Depends(get_db), _internal: bool = Depends(verify_internal_key)):
    # Llamado tras pago exitoso para confirmar la reserva del espacio
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).with_for_update().first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    
    espacio.estado = EstadoEspacio.reservado
    db.commit()
    db.refresh(espacio)
    return espacio

@router.put("/{espacio_id}/ocupar", response_model=EspacioResponse)
def marcar_espacio_ocupado(espacio_id: int, db: Session = Depends(get_db), _internal: bool = Depends(verify_internal_key)):
    # Entrada de vehículo al estacionamiento
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).with_for_update().first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    
    espacio.estado = EstadoEspacio.ocupado
    db.commit()
    db.refresh(espacio)
    return espacio

@router.put("/{espacio_id}/liberar", response_model=EspacioResponse)
def liberar_espacio(espacio_id: int, db: Session = Depends(get_db), _internal: bool = Depends(verify_internal_key)):
    # Consumido internamente cuando el pago falla, se cancela o expira la reserva
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).with_for_update().first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
    
    espacio.estado = EstadoEspacio.libre
    db.commit()
    db.refresh(espacio)
    return espacio

@router.post("/lote", response_model=List[EspacioResponse], status_code=status.HTTP_201_CREATED)
def crear_espacios_lote(lote_in: EspacioLoteCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_propietario)):
    sede = db.query(Sede).filter(Sede.id == lote_in.sede_id).first()
    if not sede:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sede no existe")
        
    if current_user.rol == "propietario" and sede.propietario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes modificar una sede que no te pertenece.")
        
    existentes = db.query(Espacio).filter(
        Espacio.sede_id == lote_in.sede_id,
        Espacio.numero.like(f"{lote_in.prefijo}%")
    ).count()
    
    nuevos_espacios = []
    for i in range(1, lote_in.cantidad + 1):
        num_correlativo = existentes + i
        num_identificador = f"{lote_in.prefijo}-{num_correlativo}"
        
        espacio = Espacio(
            sede_id=lote_in.sede_id,
            numero=num_identificador,
            tipo_vehiculo=lote_in.tipo_vehiculo or TipoVehiculo.auto,
            estado=EstadoEspacio.libre
        )
        db.add(espacio)
        nuevos_espacios.append(espacio)
        
    db.commit()
    for e in nuevos_espacios:
        db.refresh(e)
        
    return nuevos_espacios

@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(require_propietario)):
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")
        
    if current_user.rol == "propietario":
        sede = db.query(Sede).filter(Sede.id == espacio.sede_id).first()
        if sede.propietario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes eliminar espacios de una sede ajena.")
            
    db.delete(espacio)
    db.commit()
    return None
