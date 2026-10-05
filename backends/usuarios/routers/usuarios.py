from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Usuario, RolUsuario, Vehiculo, Plan, Suscripcion
from schemas import (
    UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse, 
    SSOLoginRequest, UsuarioUpdate, OperadorCreate, VehiculoCreate, 
    VehiculoResponse, PlanResponse, PlanCreate, SuscripcionResponse,
    CuentaBancariaUpdate
)
import secrets
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    if user_in.rol not in [RolUsuario.conductor, RolUsuario.propietario]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registro público no permitido: Solo se admite rol 'conductor' o 'propietario'."
        )
        
    existing = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")
    
    nuevo_usuario = Usuario(
        nombre=user_in.nombre,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        rol=user_in.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    if not usuario or not verify_password(credentials.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    if not usuario.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta inactiva. Por favor contacte al administrador.")
        
    access_token = create_access_token({"sub": usuario.id, "email": usuario.email, "rol": usuario.rol.value, "sede_id": usuario.sede_id})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse.model_validate(usuario)
    )

@router.post("/sso-login", response_model=TokenResponse)
def sso_login(payload: SSOLoginRequest, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="El inicio de sesión SSO simulado está deshabilitado por razones de seguridad. Utilice /login estándar."
    )

@router.get("/perfil", response_model=UsuarioResponse)
def obtener_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/cuenta-bancaria", response_model=UsuarioResponse)
def actualizar_cuenta_bancaria(
    payload: CuentaBancariaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != RolUsuario.propietario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los propietarios pueden configurar cuentas bancarias.")
    
    current_user.banco = payload.banco
    current_user.numero_cuenta = payload.numero_cuenta
    current_user.cci_alias = payload.cci_alias
    current_user.titular_cuenta = payload.titular_cuenta
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/propietarios/{id}/cuenta-bancaria")
def obtener_cuenta_bancaria_propietario(id: int, db: Session = Depends(get_db)):
    prop = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == RolUsuario.propietario).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    return {
        "propietario_id": prop.id,
        "nombre": prop.nombre,
        "banco": prop.banco,
        "numero_cuenta": prop.numero_cuenta,
        "cci_alias": prop.cci_alias,
        "titular_cuenta": prop.titular_cuenta
    }

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    return db.query(Usuario).all()

# CRUD Propietarios (Admin only)
@router.post("/propietarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_propietario(
    user_in: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    existing = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")
    
    nuevo_propietario = Usuario(
        nombre=user_in.nombre,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        rol=RolUsuario.propietario,
        activo=True
    )
    db.add(nuevo_propietario)
    db.commit()
    db.refresh(nuevo_propietario)
    return nuevo_propietario

@router.get("/propietarios", response_model=List[UsuarioResponse])
def listar_propietarios(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    return db.query(Usuario).filter(Usuario.rol == RolUsuario.propietario).all()

@router.put("/propietarios/{id}", response_model=UsuarioResponse)
def actualizar_propietario(
    id: int,
    user_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    usuario = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == RolUsuario.propietario).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
        
    if user_update.nombre is not None:
        usuario.nombre = user_update.nombre
    if user_update.email is not None:
        duplicado = db.query(Usuario).filter(Usuario.email == user_update.email, Usuario.id != id).first()
        if duplicado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado por otro usuario")
        usuario.email = user_update.email
    if user_update.password is not None:
        usuario.password_hash = hash_password(user_update.password)
    if user_update.activo is not None:
        usuario.activo = user_update.activo
        
    db.commit()
    db.refresh(usuario)
    return usuario

# Gestión de Operadores (Propietario/Admin only)
@router.post("/operadores", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_operador(
    operador_in: OperadorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != RolUsuario.propietario and current_user.rol != RolUsuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: Solo propietarios pueden crear operadores")
        
    if current_user.rol == RolUsuario.propietario:
        sus = db.query(Suscripcion).filter(Suscripcion.propietario_id == current_user.id, Suscripcion.estado == "activa").order_by(Suscripcion.id.desc()).first()
        if not sus:
            raise HTTPException(status_code=403, detail="Suscripción inactiva o inexistente.")
        plan = db.query(Plan).filter(Plan.id == sus.plan_id).first()
        operadores_count = db.query(Usuario).filter(Usuario.propietario_id == current_user.id, Usuario.rol == RolUsuario.operador).count()
        if operadores_count >= plan.max_operadores:
            raise HTTPException(status_code=403, detail=f"Límite de operadores alcanzado ({plan.max_operadores}) para tu plan actual.")

    existing = db.query(Usuario).filter(Usuario.email == operador_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")
        
    nuevo_operador = Usuario(
        nombre=operador_in.nombre,
        email=operador_in.email,
        password_hash=hash_password(operador_in.password),
        rol=RolUsuario.operador,
        propietario_id=current_user.id if current_user.rol == RolUsuario.propietario else None,
        sede_id=operador_in.sede_id,
        activo=True
    )
    db.add(nuevo_operador)
    db.commit()
    db.refresh(nuevo_operador)
    return nuevo_operador

@router.get("/operadores", response_model=List[UsuarioResponse])
def listar_operadores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol == RolUsuario.admin:
        return db.query(Usuario).filter(Usuario.rol == RolUsuario.operador).all()
    elif current_user.rol == RolUsuario.propietario:
        return db.query(Usuario).filter(Usuario.rol == RolUsuario.operador, Usuario.propietario_id == current_user.id).all()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

@router.put("/operadores/{id}/toggle-activo", response_model=UsuarioResponse)
def toggle_activo_operador(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    op = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == RolUsuario.operador).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operador no encontrado")
    if current_user.rol == RolUsuario.propietario and op.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes modificar un operador ajeno")
    op.activo = not op.activo
    db.commit()
    db.refresh(op)
    return op

@router.delete("/operadores/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_operador(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    op = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == RolUsuario.operador).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operador no encontrado")
    if current_user.rol == RolUsuario.propietario and op.propietario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar un operador ajeno")
    db.delete(op)
    db.commit()
    return None


# Gestión de Vehículos (Conductor)
@router.post("/vehiculos", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
def registrar_vehiculo(
    vehiculo_in: VehiculoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != RolUsuario.conductor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los conductores pueden registrar vehículos.")
        
    nuevo_vehiculo = Vehiculo(
        usuario_id=current_user.id,
        placa=vehiculo_in.placa,
        marca=vehiculo_in.marca,
        modelo=vehiculo_in.modelo,
        color=vehiculo_in.color
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

@router.get("/vehiculos", response_model=List[VehiculoResponse])
def listar_mis_vehiculos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Vehiculo).filter(Vehiculo.usuario_id == current_user.id).all()

from datetime import datetime, timedelta

# Gestión de Planes SaaS
@router.get("/planes", response_model=List[PlanResponse])
def listar_planes(db: Session = Depends(get_db)):
    return db.query(Plan).order_by(Plan.id).all()

@router.post("/planes", response_model=PlanResponse)
def crear_plan(plan_in: PlanCreate, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    nuevo_plan = Plan(**plan_in.model_dump())
    db.add(nuevo_plan)
    db.commit()
    db.refresh(nuevo_plan)
    return nuevo_plan

@router.put("/planes/{id}", response_model=PlanResponse)
def actualizar_plan(id: int, plan_in: PlanCreate, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    plan = db.query(Plan).filter(Plan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    plan.nombre = plan_in.nombre
    plan.precio = plan_in.precio
    plan.max_sedes = plan_in.max_sedes
    plan.max_operadores = plan_in.max_operadores
    plan.activo = plan_in.activo
    db.commit()
    db.refresh(plan)
    return plan

# Gestión de Suscripciones (Propietario)
@router.get("/suscripcion/actual", response_model=SuscripcionResponse)
def obtener_mi_suscripcion(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.propietario:
        raise HTTPException(status_code=403, detail="Solo para propietarios")
    sus = db.query(Suscripcion).filter(Suscripcion.propietario_id == current_user.id).order_by(Suscripcion.id.desc()).first()
    if not sus:
        raise HTTPException(status_code=404, detail="No tiene suscripción")
    return sus

import os
import httpx

PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://pagos:8004")

@router.post("/suscripcion/comprar", response_model=SuscripcionResponse)
async def comprar_suscripcion(plan_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.propietario:
        raise HTTPException(status_code=403, detail="Solo para propietarios")
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
        
    # Cancelar o marcar vencida cualquier suscripción activa anterior
    suscripciones_anteriores = db.query(Suscripcion).filter(
        Suscripcion.propietario_id == current_user.id,
        Suscripcion.estado == "activa"
    ).all()
    for s in suscripciones_anteriores:
        s.estado = "cancelada"

    nueva_sus = Suscripcion(
        propietario_id=current_user.id,
        plan_id=plan.id,
        estado="pendiente", # Se activa automáticamente tras cobrar con Culqi
        fecha_vencimiento=datetime.utcnow() + timedelta(days=30)
    )
    db.add(nueva_sus)
    db.commit()
    db.refresh(nueva_sus)

    # Registrar orden de pago pendiente en el servicio de pagos con X-Internal-Key
    pago_id_creado = None
    try:
        INTERNAL_KEY = os.getenv("INTERNAL_SERVICE_KEY", "internal_secret_microservice_key_2026")
        pago_payload = {
            "tipo": "suscripcion",
            "suscripcion_id": nueva_sus.id,
            "pagador_id": current_user.id,
            "receptor_id": None, # Plataforma/Admin recibe el pago
            "monto": float(plan.precio),
            "metodo_pago": "tarjeta",
            "estado": "pendiente"
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp_pago = await client.post(
                f"{PAGOS_SERVICE_URL}/pagos/",
                json=pago_payload,
                headers={"X-Internal-Key": INTERNAL_KEY}
            )
            if resp_pago.status_code == 201:
                pago_id_creado = resp_pago.json().get("id")
    except Exception as err:
        print(f"Advertencia: No se pudo registrar orden de pago de suscripción: {err}")

    res = SuscripcionResponse.model_validate(nueva_sus)
    res.pago_id = pago_id_creado
    return res

# Administrador supervisando membresías
@router.get("/suscripciones/todas", response_model=List[SuscripcionResponse])
def listar_todas_suscripciones(db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    return db.query(Suscripcion).order_by(Suscripcion.id.desc()).all()

@router.put("/suscripciones/{id}/estado", response_model=SuscripcionResponse)
def actualizar_estado_suscripcion(
    id: int, 
    payload: dict, 
    db: Session = Depends(get_db), 
    admin: Optional[Usuario] = Depends(lambda: None),
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")
):
    INTERNAL_KEY = os.getenv("INTERNAL_SERVICE_KEY", "internal_secret_microservice_key_2026")
    is_internal = (x_internal_key == INTERNAL_KEY)
    if not is_internal:
        if not admin or admin.rol != RolUsuario.admin:
            raise HTTPException(status_code=403, detail="Acceso denegado: se requiere rol de administrador o clave interna")
    sus = db.query(Suscripcion).filter(Suscripcion.id == id).first()
    if not sus:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    
    nuevo_estado = payload.get("estado")
    if nuevo_estado in ["activa", "cancelada", "vencida"]:
        sus.estado = nuevo_estado
    
    # Si renueva, extender 30 días adicionales
    if payload.get("extender_dias"):
        dias = int(payload.get("extender_dias"))
        sus.fecha_vencimiento = datetime.utcnow() + timedelta(days=dias)
        sus.estado = "activa"

    db.commit()
    db.refresh(sus)
    return sus

@router.put("/propietarios/{id}/toggle-activo", response_model=UsuarioResponse)
def toggle_activo_propietario(
    id: int, 
    db: Session = Depends(get_db), 
    admin: Usuario = Depends(require_admin)
):
    usuario = db.query(Usuario).filter(Usuario.id == id, Usuario.rol == RolUsuario.propietario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    usuario.activo = not usuario.activo
    db.commit()
    db.refresh(usuario)
    return usuario

@router.get("/suscripcion/limites/{propietario_id}")
def obtener_limites(propietario_id: int, db: Session = Depends(get_db)):
    sus = db.query(Suscripcion).filter(Suscripcion.propietario_id == propietario_id, Suscripcion.estado == "activa").order_by(Suscripcion.id.desc()).first()
    if not sus:
        raise HTTPException(status_code=403, detail="Suscripción inactiva o inexistente.")
    plan = db.query(Plan).filter(Plan.id == sus.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return {"max_sedes": plan.max_sedes, "max_operadores": plan.max_operadores}
