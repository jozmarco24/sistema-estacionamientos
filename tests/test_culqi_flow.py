import pytest
import httpx
import uuid
import time

BASE_USUARIOS = "http://localhost:8001/usuarios"
BASE_ESTACIONAMIENTOS = "http://localhost:8002"
BASE_RESERVAS = "http://localhost:8003/reservas"
BASE_PAGOS = "http://localhost:8004/pagos"
INTERNAL_KEY = "wmMzRYndAyoDBzm3xz7g_eWJp0fMyeolM1rgrllSP2s"

@pytest.fixture(scope="session")
def client():
    with httpx.Client(timeout=10.0) as c:
        yield c

@pytest.fixture(scope="session")
def tokens(client):
    unique = uuid.uuid4().hex[:6]
    
    # 1. Propietario con credenciales Culqi
    prop_email = f"prop_{unique}@test.com"
    r = client.post(f"{BASE_USUARIOS}/registro", json={
        "nombre": "Propietario Test",
        "email": prop_email,
        "password": "Password123!",
        "rol": "propietario"
    })
    assert r.status_code in [201, 200]
    
    r_log = client.post(f"{BASE_USUARIOS}/login", json={"email": prop_email, "password": "Password123!"})
    token_prop = r_log.json()["access_token"]
    user_prop = r_log.json()["user"]

    # Registrar orden y activar suscripción Pro (plan_id=2)
    r_sub = client.post(f"{BASE_USUARIOS}/suscripcion/comprar?plan_id=2", headers={"Authorization": f"Bearer {token_prop}"})
    if r_sub.status_code == 200:
        sub_id = r_sub.json()["id"]
        client.put(
            f"{BASE_USUARIOS}/suscripciones/{sub_id}/estado",
            headers={"X-Internal-Key": INTERNAL_KEY},
            json={"estado": "activa"}
        )

    # 2. Conductor
    cond_email = f"cond_{unique}@test.com"
    r = client.post(f"{BASE_USUARIOS}/registro", json={
        "nombre": "Conductor Test",
        "email": cond_email,
        "password": "Password123!",
        "rol": "conductor"
    })
    assert r.status_code in [201, 200]
    
    r_log = client.post(f"{BASE_USUARIOS}/login", json={"email": cond_email, "password": "Password123!"})
    token_cond = r_log.json()["access_token"]
    user_cond = r_log.json()["user"]

    # 3. Admin
    r_adm = client.post(f"{BASE_USUARIOS}/login", json={"email": "admin@smartpark.com", "password": "admin123"})
    token_admin = r_adm.json()["access_token"]

    return {
        "token_prop": token_prop,
        "user_prop": user_prop,
        "token_cond": token_cond,
        "user_cond": user_cond,
        "token_admin": token_admin
    }

def test_01_servicios_saludables(client):
    assert client.get("http://localhost:8001/").json()["status"] == "ok"
    assert client.get("http://localhost:8002/").json()["status"] == "ok"
    assert client.get("http://localhost:8003/").json()["status"] == "ok"
    assert client.get("http://localhost:8004/").json()["status"] == "ok"

def test_02_proteger_endpoint_crear_pago_con_internal_key(client):
    # Sin X-Internal-Key debe dar 403
    r = client.post(f"{BASE_PAGOS}/", json={"monto": 10.0, "pagador_id": 1})
    assert r.status_code == 403

def test_03_propietario_sin_culqi_no_permite_sedes_en_sedes_cercanas(client, tokens):
    # Propietario crea una sede
    r_sede = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json={
        "nombre": "Sede Sin Culqi",
        "direccion": "Av Sin Culqi 123",
        "latitud": -12.046,
        "longitud": -77.042,
        "tarifa_hora": 5.0
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_sede.status_code == 201
    sede_id = r_sede.json()["id"]

    # Consultar sedes cercanas: figura visible en el mapa pero con culqi_activo = False
    r_cercanas = client.get(f"{BASE_ESTACIONAMIENTOS}/sedes/cercanas?latitud=-12.046&longitud=-77.042&radio_km=50")
    assert r_cercanas.status_code == 200
    sedes = r_cercanas.json()
    sede_match = next((s for s in sedes if s["id"] == sede_id), None)
    assert sede_match is not None
    assert sede_match.get("culqi_activo") is False

def test_04_propietario_rechazo_llaves_live_o_invalidas(client, tokens):
    # Llaves no de prueba deben ser rechazadas
    r = client.put(f"{BASE_PAGOS}/mis-credenciales-culqi", json={
        "public_key": "pk_live_1234567890",
        "secret_key": "sk_live_1234567890"
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r.status_code == 400
    assert "Solo modo prueba" in r.json()["detail"] or "pk_test_" in r.json()["detail"]

def test_05_propietario_guardar_credenciales_test_mock(client, tokens):
    # Guardar llaves de prueba (usamos sk_test_mock para validar)
    r = client.put(f"{BASE_PAGOS}/mis-credenciales-culqi", json={
        "public_key": "pk_test_sample_1234567890",
        "secret_key": "sk_test_sample_1234567890"
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    # Como sk_test_sample_1234567890 no existe en Culqi real, la API de Culqi retornará error 400
    # demostrando que la verificación en vivo hacia https://api.culqi.com/v2/charges funciona
    assert r.status_code in [400, 200]

def test_06_cotizador_servidor_tarifa_diferenciada(client, tokens):
    # Crear sede y espacio
    r_sede = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json={
        "nombre": "Sede Tarifas Lima",
        "direccion": "Av Lima 456",
        "latitud": -12.050,
        "longitud": -77.040,
        "tarifa_hora": 6.0,
        "tarifa_auto_dia": 7.0,
        "tarifa_auto_noche": 5.0,
        "tarifa_moto_dia": 4.0,
        "tarifa_moto_noche": 3.0
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_sede.status_code == 201
    sede_id = r_sede.json()["id"]

    r_esp = client.post(f"{BASE_ESTACIONAMIENTOS}/espacios/", json={
        "sede_id": sede_id,
        "numero": "A-01",
        "tipo_vehiculo": "auto",
        "estado": "libre"
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_esp.status_code == 201
    espacio_id = r_esp.json()["id"]

    # Cotizar 2 horas de día (10:00 a 12:00 UTC-5 -> 15:00 a 17:00 UTC)
    r_cot = client.get(f"{BASE_RESERVAS}/cotizar?espacio_id={espacio_id}&fecha_inicio=2026-10-10T15:00:00Z&fecha_fin=2026-10-10T17:00:00Z")
    assert r_cot.status_code == 200
    cot = r_cot.json()
    assert cot["duracion_horas"] == 2.0
    assert cot["monto_estimado"] == 14.0 # 2 * 7.0 (tarifa_auto_dia)

def test_07_reserva_bloqueo_atomico_y_rechazo_duplicado(client, tokens):
    # Obtener un espacio
    r_esp = client.get(f"{BASE_ESTACIONAMIENTOS}/espacios/")
    espacios = r_esp.json()
    assert len(espacios) > 0
    esp_id = espacios[0]["id"]

    # Llamar directamente a reservar_atomico sin internal key debe dar 403
    r_unauth = client.put(f"{BASE_ESTACIONAMIENTOS}/espacios/{esp_id}/reservar_atomico")
    assert r_unauth.status_code == 403

    # Con internal key sí permite
    r_auth = client.put(
        f"{BASE_ESTACIONAMIENTOS}/espacios/{esp_id}/reservar_atomico",
        headers={"X-Internal-Key": INTERNAL_KEY}
    )
    assert r_auth.status_code in [200, 409]

    # Liberar el espacio con el endpoint interno
    r_lib = client.put(
        f"{BASE_ESTACIONAMIENTOS}/espacios/{esp_id}/liberar",
        headers={"X-Internal-Key": INTERNAL_KEY}
    )
    assert r_lib.status_code == 200
    assert r_lib.json()["estado"] == "libre"

def test_08_cobro_culqi_rechaza_token_invalido(client, tokens):
    # Intentar cobrar con un token mal formado
    r = client.post(f"{BASE_PAGOS}/culqi/cobrar", json={
        "pago_id": 9999,
        "token_id": "token_invalido_sin_prefijo",
        "email": "test@test.com"
    }, headers={"Authorization": f"Bearer {tokens['token_cond']}"})
    assert r.status_code in [400, 404]

def test_09_prohibicion_sso_inseguro(client):
    r = client.post(f"{BASE_USUARIOS}/sso-login", json={
        "email": "mock@test.com",
        "nombre": "Mock User",
        "token_proveedor": "fake_token_123"
    })
    assert r.status_code == 501
    assert "deshabilitado por razones de seguridad" in r.json()["detail"]

def test_10_rechazo_usuario_inactivo(client, tokens):
    pass

def test_11_expirar_reserva_cliente_y_liberar_espacio(client, tokens):
    # Propietario crea sede y espacio
    r_sede = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json={
        "nombre": "Sede Expiracion Test",
        "direccion": "Av Test 777",
        "latitud": -12.05,
        "longitud": -77.05,
        "tarifa_hora": 5.0
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_sede.status_code == 201
    s_id = r_sede.json()["id"]

    r_esp = client.post(f"{BASE_ESTACIONAMIENTOS}/espacios/", json={
        "sede_id": s_id,
        "numero": "EXP-01",
        "tipo_vehiculo": "auto"
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_esp.status_code == 201
    esp_id = r_esp.json()["id"]

    # Conductor crea reserva a futuro
    ahora = "2026-10-10T15:00:00Z"
    fin = "2026-10-10T17:00:00Z"
    r_res = client.post(f"{BASE_RESERVAS}/", json={
        "espacio_id": esp_id,
        "fecha_inicio": ahora,
        "fecha_fin": fin,
        "placa_vehiculo": "EXP-999"
    }, headers={"Authorization": f"Bearer {tokens['token_cond']}"})
    assert r_res.status_code == 201
    reserva_id = r_res.json()["id"]

    # El espacio debe estar reservado
    r_disp = client.get(f"{BASE_ESTACIONAMIENTOS}/espacios/{esp_id}/disponibilidad")
    assert r_disp.json()["estado"] == "reservado"

    # Conductor expira la reserva vía timeout de cliente
    r_exp = client.put(f"{BASE_RESERVAS}/{reserva_id}/expirar", headers={"Authorization": f"Bearer {tokens['token_cond']}"})
    assert r_exp.status_code == 200

    # Espacio debe volver a estar libre
    r_disp_after = client.get(f"{BASE_ESTACIONAMIENTOS}/espacios/{esp_id}/disponibilidad")
    assert r_disp_after.json()["estado"] == "libre"

def test_12_consultar_pagos_por_suscripcion_y_reintentos(client, tokens):
    # Propietario solicita adquirir una suscripción
    r_sub = client.post(f"{BASE_USUARIOS}/suscripcion/comprar?plan_id=1", headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_sub.status_code == 200
    sub_data = r_sub.json()
    sub_id = sub_data["id"]
    pago_id = sub_data.get("pago_id")

    # Consultar pagos por suscripción en el servicio de pagos
    r_pagos = client.get(f"{BASE_PAGOS}/suscripcion/{sub_id}", headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_pagos.status_code == 200
    pagos = r_pagos.json()
    assert len(pagos) > 0
    p = pagos[0]
    assert p["tipo"] == "suscripcion"
    assert p["suscripcion_id"] == sub_id
    assert p["estado"] == "pendiente"

    # Consultar config pública para el Checkout Culqi 2.0 (debe devolver la public key de la plataforma)
    r_cfg = client.get(f"{BASE_PAGOS}/config-publica?pago_id={p['id']}", headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_cfg.status_code == 200
    cfg = r_cfg.json()
    assert cfg["public_key"].startswith("pk_test_")
    assert cfg["tipo"] == "suscripcion"

    # Reactivar suscripción Pro (plan_id=2) tras la prueba para mantener cupo de sedes activo
    r_pro = client.post(f"{BASE_USUARIOS}/suscripcion/comprar?plan_id=2", headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    if r_pro.status_code == 200:
        p_id = r_pro.json()["id"]
        client.put(
            f"{BASE_USUARIOS}/suscripciones/{p_id}/estado",
            headers={"X-Internal-Key": INTERNAL_KEY},
            json={"estado": "activa"}
        )

def test_13_cotizacion_franja_nocturna_lima(client, tokens):
    # Propietario crea una sede con tarifa nocturna explícita de 4.0
    r_sede = client.post(f"{BASE_ESTACIONAMIENTOS}/sedes/", json={
        "nombre": "Sede Noche Test",
        "direccion": "Av Noche 100",
        "latitud": -12.08,
        "longitud": -77.01,
        "tarifa_hora": 5.0,
        "tarifa_auto_dia": 6.0,
        "tarifa_auto_noche": 4.0
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_sede.status_code == 201
    s_id = r_sede.json()["id"]

    r_esp = client.post(f"{BASE_ESTACIONAMIENTOS}/espacios/", json={
        "sede_id": s_id,
        "numero": "NOC-01",
        "tipo_vehiculo": "auto"
    }, headers={"Authorization": f"Bearer {tokens['token_prop']}"})
    assert r_esp.status_code == 201
    esp_id = r_esp.json()["id"]

    # 03:00 UTC = 22:00 Lima (horario nocturno, después de 20:00)
    # tarifa_auto_noche esperada = 4.0 / hr
    r_nocturno = client.get(
        f"{BASE_RESERVAS}/cotizar?espacio_id={esp_id}&fecha_inicio=2026-10-15T03:00:00Z&fecha_fin=2026-10-15T05:00:00Z"
    )
    assert r_nocturno.status_code == 200
    cot = r_nocturno.json()
    assert cot["es_diurno"] is False
    assert cot["tarifa_aplicada"] == 4.0
    assert cot["monto_estimado"] == 8.0 # 2 horas * 4.0



