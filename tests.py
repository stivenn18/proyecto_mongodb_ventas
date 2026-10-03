import pytest
from wishlist import WishlistService


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
