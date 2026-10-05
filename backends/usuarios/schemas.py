from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import RolUsuario

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: Optional[RolUsuario] = RolUsuario.conductor

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: RolUsuario
    creado_en: datetime
    activo: bool
    propietario_id: Optional[int] = None
    sede_id: Optional[int] = None
    banco: Optional[str] = None
    numero_cuenta: Optional[str] = None
    cci_alias: Optional[str] = None
    titular_cuenta: Optional[str] = None

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    activo: Optional[bool] = None
    banco: Optional[str] = None
    numero_cuenta: Optional[str] = None
    cci_alias: Optional[str] = None
    titular_cuenta: Optional[str] = None

class CuentaBancariaUpdate(BaseModel):
    banco: str
    numero_cuenta: str
    cci_alias: Optional[str] = None
    titular_cuenta: str

class OperadorCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    sede_id: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse

class SSOLoginRequest(BaseModel):
    email: EmailStr
    nombre: str
    token_proveedor: str

class VehiculoBase(BaseModel):
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    color: Optional[str] = None

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoResponse(VehiculoBase):
    id: int
    usuario_id: int
    class Config:
        from_attributes = True

class PlanBase(BaseModel):
    nombre: str
    precio: float
    max_sedes: int
    max_operadores: int
    activo: Optional[bool] = True

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id: int
    class Config:
        from_attributes = True

class SuscripcionResponse(BaseModel):
    id: int
    propietario_id: int
    plan_id: int
    estado: str
    fecha_inicio: datetime
    fecha_vencimiento: datetime
    pago_id: Optional[int] = None
    class Config:
        from_attributes = True
