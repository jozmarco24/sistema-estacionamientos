import pytest
import httpx
import uuid
import os

BASE_USUARIOS = os.getenv("USUARIOS_SERVICE_URL", "http://localhost:8001/usuarios")
BASE_ESTACIONAMIENTOS = os.getenv("ESTACIONAMIENTOS_SERVICE_URL", "http://localhost:8002")
INTERNAL_KEY = os.getenv("INTERNAL_SERVICE_KEY", "93b44a5e7bc28ceee2c12f37354b3b87b3995447d4934b659fbe03b3d67a2977")

@pytest.fixture(scope="session")
def client():
    with httpx.Client(timeout=10.0) as c:
        yield c

def registrar_propietario(client, plan_id: int):
    """Crea un propietario de prueba con un plan específico activado."""
    unique = uuid.uuid4().hex[:6]
    prop_email = f"saas_prop_{unique}@test.com"
    r = client.post(f"{BASE_USUARIOS}/registro", json={
        "nombre": f"Propietario Plan {plan_id}",
        "email": prop_email,
        "password": "Password123!",
        "rol": "propietario"
    })
    assert r.status_code in [201, 200], f"Fallo al registrar usuario: {r.text}"

    r_log = client.post(f"{BASE_USUARIOS}/login", json={"email": prop_email, "password": "Password123!"})
    token = r_log.json()["access_token"]
    user_info = r_log.json()["user"]

    # Activar suscripción con el plan deseado (ej. plan_id=1 -> max_sedes=1)
    r_sub = client.post(
        f"{BASE_USUARIOS}/suscripcion/comprar?plan_id={plan_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if r_sub.status_code == 200:
        sub_id = r_sub.json()["id"]
        # Activar mediante endpoint interno con X-Internal-Key
        r_act = client.put(
            f"{BASE_USUARIOS}/suscripciones/{sub_id}/estado",
            headers={"X-Internal-Key": INTERNAL_KEY},
            json={"estado": "activa"}
        )
        assert r_act.status_code == 200, f"No se pudo activar suscripción: {r_act.text}"

    return token, user_info


def test_saas_limite_max_sedes_plan_basico(client):
    """
    Test de límite SaaS:
    1. Un propietario con Plan Básico (plan_id=1, max_sedes=1) registra 1 sede exitosamente (201).
    2. Al intentar registrar una segunda sede, el servicio de estacionamientos
       debe bloquear la creación respondiendo 403 Forbidden por exceder max_sedes.
    """
    token, user = registrar_propietario(client, plan_id=1)
    headers = {"Authorization": f"Bearer {token}"}

    # Verificar que el servicio usuarios devuelve el límite configurado
    r_limites = client.get(
        f"{BASE_USUARIOS}/suscripcion/limites/{user['id']}",
        headers={"X-Internal-Key": INTERNAL_KEY}
    )
    assert r_limites.status_code == 200
    limites = r_limites.json()
    assert "max_sedes" in limites
    max_sedes = limites["max_sedes"]
    assert max_sedes == 1, f"Se esperaba max_sedes=1 para Plan Básico, se obtuvo {max_sedes}"

    # 1. Crear la primera sede (debe ser exitoso dentro del límite permitido)
    sede_1 = {
        "nombre": "Sede Central Permitida",
        "direccion": "Av. Principal 101",
        "latitud": -12.046374,
        "longitud": -77.042793,
        "tarifa_hora": 5.0,
        "capacidad_total": 20
    }
    r1 = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json=sede_1, headers=headers)
    assert r1.status_code == 201, f"La creación de la primera sede falló: {r1.status_code} - {r1.text}"

    # 2. Intentar crear una segunda sede que exceda el límite permitido (max_sedes = 1)
    sede_2 = {
        "nombre": "Sede Excedente Rechazada",
        "direccion": "Av. Secundaria 202",
        "latitud": -12.050000,
        "longitud": -77.040000,
        "tarifa_hora": 6.0,
        "capacidad_total": 15
    }
    r2 = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json=sede_2, headers=headers)
    assert r2.status_code == 403, f"Se esperaba 403 Forbidden por superar max_sedes, se obtuvo {r2.status_code}: {r2.text}"
    assert "Límite de sedes alcanzado" in r2.json().get("detail", "")


def test_saas_propietario_sin_suscripcion_activa_rechazado(client):
    """
    Test de seguridad SaaS:
    Un propietario sin suscripción activa debe recibir 403 al intentar crear una sede.
    """
    unique = uuid.uuid4().hex[:6]
    prop_email = f"sin_sub_{unique}@test.com"
    r = client.post(f"{BASE_USUARIOS}/registro", json={
        "nombre": "Propietario Sin Plan",
        "email": prop_email,
        "password": "Password123!",
        "rol": "propietario"
    })
    assert r.status_code in [201, 200]

    r_log = client.post(f"{BASE_USUARIOS}/login", json={"email": prop_email, "password": "Password123!"})
    token = r_log.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sede_data = {
        "nombre": "Sede Sin Suscripción",
        "direccion": "Av. No Valida 999",
        "latitud": -12.046374,
        "longitud": -77.042793,
        "tarifa_hora": 4.0,
        "capacidad_total": 10
    }
    r = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json=sede_data, headers=headers)
    assert r.status_code == 403
    assert "suscripción" in r.json().get("detail", "").lower()
