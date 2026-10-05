from database import SessionLocal
from models import Usuario, RolUsuario
from auth import hash_password

db = SessionLocal()

users = [
    {"nombre": "Administrador Demo", "email": "admin@demo.com", "password": "password123", "rol": RolUsuario.admin},
    {"nombre": "Propietario Demo", "email": "propietario@demo.com", "password": "password123", "rol": RolUsuario.propietario},
    {"nombre": "Operador Demo", "email": "operador@demo.com", "password": "password123", "rol": RolUsuario.operador},
    {"nombre": "Cliente Demo", "email": "cliente@demo.com", "password": "password123", "rol": RolUsuario.conductor}
]

for u in users:
    if not db.query(Usuario).filter(Usuario.email == u["email"]).first():
        db_user = Usuario(
            nombre=u["nombre"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            rol=u["rol"]
        )
        db.add(db_user)

db.commit()
db.close()
print("Usuarios de prueba creados con éxito.")
