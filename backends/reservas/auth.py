import os
import jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET no está configurado. El servicio no puede arrancar sin esta variable.")
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

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requieren privilegios de administrador")
    return current_user

def require_conductor(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.rol not in ["conductor", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere cuenta de conductor")
    return current_user

def verify_internal_key(x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")):
    if not INTERNAL_SERVICE_KEY or x_internal_key != INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso interno denegado: clave inter-servicio inválida"
        )
    return True
