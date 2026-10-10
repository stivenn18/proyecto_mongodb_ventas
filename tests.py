import pytest
from fastapi.testclient import TestClient
from app import app
from wishlist import WishlistService

client = TestClient(app)


def test_index_and_static_files():
    """Validar que index.html, style.css y script.js se sirvan correctamente para Render"""
    r_index = client.get("/")
    assert r_index.status_code == 200

    r_css = client.get("/style.css")
    assert r_css.status_code == 200
    assert "text/css" in r_css.headers["content-type"]

    r_js = client.get("/script.js")
    assert r_js.status_code == 200
    assert "javascript" in r_js.headers["content-type"]

    r_miro = client.get("/miro")
    assert r_miro.status_code == 200
    assert "text/html" in r_miro.headers["content-type"]


def test_health_check_endpoint():
    """Validar que el endpoint /health responde con status healthy para Render"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ventas-wishlist-api"


def test_api_flags_endpoint():
    """Validar consulta de Feature Flags"""
    response = client.get("/api/flags")
    assert response.status_code == 200
    data = response.json()
    assert "wishlist_enabled" in data
    assert "pagos_express_v1" in data


def test_pagos_express_desactivado_por_defecto():
    """Caso Taller 6: Validar que pagos-express-v1 en OFF (0% rollout) bloquea la transacción con 403"""
    payload = {"cliente_id": "CLI001", "sku": "PROD001", "monto": 4500000.0}
    response = client.post("/api/pagos-express", json=payload)
    assert response.status_code == 403
    assert "deshabilitada" in response.json()["detail"]


def test_wishlist_flag_desactivado():
    """Validar que si el flag está apagado (0% rollout), el servicio no procesa la wishlist"""
    service = WishlistService(feature_flag_enabled=False)
    producto = {"sku": "PROD001", "nombre": "Laptop Dell XPS 15", "precio_unitario": 4500000}
    resultado = service.agregar_producto_deseo("CLI001", producto)
    assert resultado["status"] == "disabled"
    assert service.obtener_deseos("CLI001") == []


def test_wishlist_flag_activo_agregar():
    """Validar agregar producto a la lista de deseos cuando el flag está activo"""
    service = WishlistService(feature_flag_enabled=True)
    producto = {
        "sku": "PROD001",
        "nombre": "Laptop Dell XPS 15",
        "precio_unitario": 4500000,
        "categoria": "Electrónica"
    }
    resultado = service.agregar_producto_deseo("CLI001", producto)
    assert resultado["status"] == "success"

    deseos = service.obtener_deseos("CLI001")
    assert len(deseos) == 1
    assert deseos[0]["sku"] == "PROD001"


def test_wishlist_eliminar_producto():
    """Validar eliminación de producto de la lista de deseos"""
    service = WishlistService(feature_flag_enabled=True)
    producto = {"sku": "PROD002", "nombre": "Mouse Inalámbrico", "precio_unitario": 120000}
    service.agregar_producto_deseo("CLI001", producto)
    assert len(service.obtener_deseos("CLI001")) == 1

    eliminado = service.eliminar_deseo("CLI001", "PROD002")
    assert eliminado is True
    assert len(service.obtener_deseos("CLI001")) == 0


def test_wishlist_datos_invalidos():
    """Validar excepción ante datos incompletos"""
    service = WishlistService(feature_flag_enabled=True)
    with pytest.raises(ValueError, match="Datos de cliente o producto inválidos."):
        service.agregar_producto_deseo("", {})
