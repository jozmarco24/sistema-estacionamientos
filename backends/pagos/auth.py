import os
import jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_jwt_key_estacionamientos_2026")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

security = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    id: int
    email: str
    rol: str
    sede_id: Optional[int] = None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> CurrentUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw_sub = payload.get("sub")
        raw_id = payload.get("id")
        user_id = raw_id if raw_id is not None else raw_sub
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = 0
            
        email = payload.get("email", "")
        rol = payload.get("rol", "")
        sede_id = payload.get("sede_id", None)
        if not user_id and not raw_sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return CurrentUser(id=user_id, email=email, rol=rol, sede_id=sede_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[CurrentUser]:
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requieren privilegios de administrador")
    return current_user

def require_propietario(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.rol not in ["admin", "propietario"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol de propietario")
    return current_user

def verify_internal_key(x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")):
    if not INTERNAL_SERVICE_KEY or x_internal_key != INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso interno denegado: clave inter-servicio inválida"
        )
    return True

def require_propietario_o_admin(current_user: CurrentUser = Depends(get_current_user)):
    if current_user.rol not in ("propietario", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a propietarios y administradores."
        )
    return current_user
