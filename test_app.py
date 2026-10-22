"""
test_app.py
-----------
Pruebas unitarias de la Entrega 2 (Integracion Continua).

Objetivo: validar automaticamente los 2 endpoints + la seguridad por token,
SIN depender de PostgreSQL. Para eso usamos:

  - El TEST CLIENT de Flask: un cliente HTTP "falso" que llama a la app en
    memoria (sin levantar un servidor real ni abrir puertos).
  - SQLite EN MEMORIA ("sqlite:///:memory:"): una base de datos que vive solo
    durante la prueba y desaparece al terminar. Asi cada corrida arranca limpia
    y no necesitamos RDS.

Se corre con:  pytest -v
"""
import pytest

from application import create_app
from models import db


# Token valido (debe coincidir con STATIC_BEARER_TOKEN de config.py).
TOKEN = "token-secreto-entrega-1-2026"
# Cabecera de autorizacion lista para reutilizar en las pruebas.
AUTH = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture
def client():
    """
    FIXTURE de pytest.

    Una "fixture" prepara lo que la prueba necesita y lo entrega. pytest la
    inyecta automaticamente en cualquier prueba que reciba un parametro
    llamado 'client'.

    Aqui:
      1. Creamos la app.
      2. La reconfiguramos para usar SQLite EN MEMORIA (en vez del archivo
         blacklist.db), asi las pruebas no tocan datos reales.
      3. Creamos las tablas en esa base temporal.
      4. Entregamos (yield) el test client a la prueba.
      5. Al terminar, limpiamos las tablas.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()          # crea la tabla 'blacklist' en memoria
        with app.test_client() as c:
            yield c              # <-- aqui corre cada prueba
        db.session.remove()
        db.drop_all()            # limpia al terminar


# --- Prueba 1: POST con token valido -> 201 (creado) ---
def test_post_blacklist_con_token_ok(client):
    """Con token y datos correctos, el email se agrega (201)."""
    resp = client.post(
        "/blacklists",
        json={"email": "malo@test.com", "app_uuid": "app-123"},
        headers=AUTH,
    )
    assert resp.status_code == 201
    # El cuerpo de respuesta confirma el email agregado.
    assert resp.get_json()["email"] == "malo@test.com"


# --- Prueba 2: POST sin token -> 401 (no autorizado) ---
def test_post_blacklist_sin_token_401(client):
    """Sin cabecera Authorization, el endpoint debe rechazar con 401."""
    resp = client.post(
        "/blacklists",
        json={"email": "malo@test.com", "app_uuid": "app-123"},
        # Ojo: NO mandamos headers=AUTH a proposito.
    )
    assert resp.status_code == 401


# --- Prueba 3: GET de un email que SI esta bloqueado -> blacklisted: true ---
def test_get_blacklist_bloqueado_true(client):
    """
    Primero agregamos el email (POST), luego lo consultamos (GET).
    Como existe, la respuesta debe decir blacklisted: true.
    """
    client.post(
        "/blacklists",
        json={"email": "bloqueado@test.com", "app_uuid": "app-123",
              "blocked_reason": "fraude"},
        headers=AUTH,
    )
    resp = client.get("/blacklists/bloqueado@test.com", headers=AUTH)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["blacklisted"] is True
    assert data["blocked_reason"] == "fraude"


# --- Prueba 4: GET de un email que NO esta bloqueado -> blacklisted: false ---
def test_get_blacklist_no_bloqueado_false(client):
    """Un email que nunca se agrego debe devolver blacklisted: false."""
    resp = client.get("/blacklists/inexistente@test.com", headers=AUTH)
    assert resp.status_code == 200
    assert resp.get_json()["blacklisted"] is False


# --- Prueba 5: GET / (health check) -> 200 ---
def test_health_ok(client):
    """El endpoint de salud responde 200 y no requiere token."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
