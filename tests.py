from unittest.mock import MagicMock, patch
from conexion import conectar_mongodb


def test_imports():
    import conexion
    assert hasattr(conexion, "conectar_mongodb")


@patch("conexion.pymongo.MongoClient")
def test_conectar_mongodb_exitoso(mock_client):
    mock_instance = MagicMock()
    mock_instance.admin.command.return_value = {"ok": 1}
    mock_client.return_value = mock_instance

    client, db = conectar_mongodb()
    assert client is not None
    assert db is not None

