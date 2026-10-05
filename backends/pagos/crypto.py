import os
from cryptography.fernet import Fernet
from fastapi import HTTPException, status

FERNET_KEY = os.getenv("FERNET_KEY") or os.getenv("ENCRYPTION_KEY", "")
ENCRYPTION_KEY = FERNET_KEY

def get_fernet() -> Fernet:
    if not FERNET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración del servidor: FERNET_KEY o ENCRYPTION_KEY no está configurada."
        )
    try:
        return Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inicializar cifrado de credenciales: {str(e)}"
        )

def cifrar(texto: str) -> str:
    return get_fernet().encrypt(texto.encode()).decode()

def descifrar(texto_cifrado: str) -> str:
    return get_fernet().decrypt(texto_cifrado.encode()).decode()

def encrypt_secret_key(secret_key: str) -> str:
    return cifrar(secret_key)

def decrypt_secret_key(encrypted_secret_key: str) -> str:
    return descifrar(encrypted_secret_key)
