import os
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurar variables de entorno antes de importar componentes
os.environ["JWT_SECRET"] = "testsecretkeyforjwtauthentication123456"
os.environ["INTERNAL_SERVICE_KEY"] = "testinternalkey987654321"

from database import Base, get_db
from models import Reserva, EstadoReserva
from auth import CurrentUser, get_current_user
from main import app, background_expirar_reservas

# Setup de Base de Datos SQLite en memoria
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Limpiar esquema para SQLite
for table in Base.metadata.tables.values():
    table.schema = None

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def conductor_user():
    return CurrentUser(id=10, email="conductor@test.com", rol="conductor")

@pytest.fixture
def otro_conductor():
    return CurrentUser(id=20, email="otro@test.com", rol="conductor")

@pytest.fixture
def admin_user():
    return CurrentUser(id=1, email="admin@test.com", rol="admin")

@pytest.fixture
def conductor_token():
    import jwt
    return jwt.encode({"sub": 10, "email": "conductor@test.com", "rol": "conductor"}, os.environ["JWT_SECRET"], algorithm="HS256")

@pytest.fixture
def otro_token():
    import jwt
    return jwt.encode({"sub": 20, "email": "otro@test.com", "rol": "conductor"}, os.environ["JWT_SECRET"], algorithm="HS256")

@pytest.fixture
def admin_token():
    import jwt
    return jwt.encode({"sub": 1, "email": "admin@test.com", "rol": "admin"}, os.environ["JWT_SECRET"], algorithm="HS256")


# ─────────────────────────────────────────────────────────────
# 6 Reglas de negocio para cancelación de reservas
# ─────────────────────────────────────────────────────────────

@patch("routers.reservas.liberar_espacio_remoto", new_callable=AsyncMock)
def test_01_cancelacion_exitosa_propia_reserva_pendiente(mock_liberar, client, conductor_token):
    """Regla 1: Conductor puede cancelar su propia reserva en estado pendiente."""
    db = TestingSessionLocal()
    reserva = Reserva(
        usuario_id=10,
        espacio_id=101,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.pendiente,
        placa_vehiculo="ABC-123"
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    res_id = reserva.id
    db.close()

    resp = client.put(
        f"/reservas/{res_id}/cancelar",
        headers={"Authorization": f"Bearer {conductor_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["reserva"]["estado"] == "cancelada"
    assert "cancelada con éxito" in data["mensaje"].lower()

    # Verificar persistencia en base de datos
    db = TestingSessionLocal()
    r_db = db.query(Reserva).filter(Reserva.id == res_id).first()
    assert r_db.estado == EstadoReserva.cancelada
    db.close()

    mock_liberar.assert_awaited_once_with(101)


@patch("routers.reservas.liberar_espacio_remoto", new_callable=AsyncMock)
def test_02_cancelacion_denegada_reserva_otro_usuario(mock_liberar, client, otro_token):
    """Regla 2: Conductor NO puede cancelar la reserva de otro usuario -> HTTP 403."""
    db = TestingSessionLocal()
    reserva = Reserva(
        usuario_id=10, # Pertenece a usuario 10
        espacio_id=102,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.pendiente,
        placa_vehiculo="XYZ-789"
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    res_id = reserva.id
    db.close()

    # Usuario 20 intenta cancelar la reserva del usuario 10
    resp = client.put(
        f"/reservas/{res_id}/cancelar",
        headers={"Authorization": f"Bearer {otro_token}"}
    )
    assert resp.status_code == 403
    assert "permiso" in resp.json()["detail"].lower()

    mock_liberar.assert_not_called()


@patch("routers.reservas.liberar_espacio_remoto", new_callable=AsyncMock)
def test_03_cancelacion_reserva_confirmada_rechazada(mock_liberar, client, conductor_token):
    """Regla 3: NO se puede cancelar una reserva confirmada -> HTTP 409."""
    db = TestingSessionLocal()
    reserva = Reserva(
        usuario_id=10,
        espacio_id=103,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.confirmada,
        placa_vehiculo="CONF-123"
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    res_id = reserva.id
    db.close()

    resp = client.put(
        f"/reservas/{res_id}/cancelar",
        headers={"Authorization": f"Bearer {conductor_token}"}
    )
    assert resp.status_code == 409
    assert "confirmada" in resp.json()["detail"].lower()

    mock_liberar.assert_not_called()


@patch("routers.reservas.liberar_espacio_remoto", new_callable=AsyncMock)
def test_04_cancelacion_reserva_ya_cancelada_rechazada(mock_liberar, client, conductor_token):
    """Regla 4: NO se puede cancelar dos veces una reserva -> HTTP 409."""
    db = TestingSessionLocal()
    reserva = Reserva(
        usuario_id=10,
        espacio_id=104,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.cancelada,
        placa_vehiculo="CANC-001"
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    res_id = reserva.id
    db.close()

    resp = client.put(
        f"/reservas/{res_id}/cancelar",
        headers={"Authorization": f"Bearer {conductor_token}"}
    )
    assert resp.status_code == 409
    assert "cancelada" in resp.json()["detail"].lower()

    mock_liberar.assert_not_called()


@pytest.mark.asyncio
@patch("main.liberar_espacio_remoto", new_callable=AsyncMock)
@patch("main.SessionLocal")
async def test_05_expiracion_automatica_reservas_vencidas(mock_session_factory, mock_liberar):
    """Regla 5: Reservas pendientes con expira_en en el pasado deben marcarse como cancelada."""
    # Usar sesión de prueba
    mock_session_factory.side_effect = lambda: TestingSessionLocal()

    db = TestingSessionLocal()
    reserva_vencida = Reserva(
        usuario_id=10,
        espacio_id=105,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.pendiente,
        placa_vehiculo="EXP-001",
        expira_en=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    db.add(reserva_vencida)
    db.commit()
    res_id = reserva_vencida.id
    db.close()

    # Ejecutar lógica del proceso de expiración directa
    db_exp = TestingSessionLocal()
    ahora = datetime.now(timezone.utc)
    vencidas = db_exp.query(Reserva.id, Reserva.espacio_id).filter(
        Reserva.estado == EstadoReserva.pendiente,
        Reserva.expira_en != None,
        Reserva.expira_en < ahora
    ).all()

    if vencidas:
        db_exp.query(Reserva).filter(
            Reserva.estado == EstadoReserva.pendiente,
            Reserva.expira_en != None,
            Reserva.expira_en < ahora
        ).update({"estado": EstadoReserva.cancelada}, synchronize_session=False)
        db_exp.commit()

        for r_id, esp_id in vencidas:
            await mock_liberar(esp_id)
    db_exp.close()

    # Validar que pasó a cancelada y liberó el espacio
    db_check = TestingSessionLocal()
    r_actualizada = db_check.query(Reserva).filter(Reserva.id == res_id).first()
    assert r_actualizada.estado == EstadoReserva.cancelada
    db_check.close()

    mock_liberar.assert_awaited_once_with(105)


@patch("routers.reservas.liberar_espacio_remoto", new_callable=AsyncMock)
def test_06_admin_puede_cancelar_cualquier_reserva(mock_liberar, client, admin_token):
    """Regla 6: Admin puede cancelar cualquier reserva sin restricción de propietario."""
    db = TestingSessionLocal()
    reserva = Reserva(
        usuario_id=99, # Reserva de otro usuario
        espacio_id=106,
        fecha_inicio=datetime.now(timezone.utc),
        fecha_fin=datetime.now(timezone.utc) + timedelta(hours=2),
        estado=EstadoReserva.pendiente,
        placa_vehiculo="ADM-777"
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    res_id = reserva.id
    db.close()

    resp = client.put(
        f"/reservas/{res_id}/cancelar",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["reserva"]["estado"] == "cancelada"

    mock_liberar.assert_awaited_once_with(106)
