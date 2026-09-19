from datetime import datetime
import os
import sys
import dns.resolver
from dotenv import load_dotenv
import pymongo

sys.stdout.reconfigure(encoding='utf-8')

try:
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1']
except Exception:
    pass

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")


def crear_estructura_ventas():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["ventas_db"]

    print("🏗 Creando estructura de base de datos de ventas...\n")

    # 1. Crear colecciones OLTP (Transaccionales)
    print("📦 Creando colecciones transaccionales (OLTP)...")
    colecciones_oltp = ["clientes", "productos", "ventas"]
    for col in colecciones_oltp:
        if col not in db.list_collection_names():
            db.create_collection(col)
        print(f"  ✅ Colección '{col}' creada")

    # 2. Crear índices para optimizar consultas
    print("\n🔍 Creando índices...")
    db.clientes.create_index([("email", 1)], unique=True)
    db.productos.create_index([("sku", 1)], unique=True)
    db.ventas.create_index([("fecha_venta", -1)])
    db.ventas.create_index([("cliente_id", 1)])
    print("  ✅ Índices creados")

    # 3. Insertar datos de prueba
    print("\n📝 Insertando datos de prueba...")
    cliente_ejemplo = {
        "codigo_cliente": "CLI001",
        "nombre": "Juan Pérez",
        "email": "juan.perez@email.com",
        "telefono": "3001234567",
        "direccion": {
            "calle": "Calle 123 #45-67",
            "ciudad": "Bogotá",
            "pais": "Colombia"
        },
        "fecha_registro": datetime.now(),
        "activo": True
    }
    try:
        db.clientes.insert_one(cliente_ejemplo)
        print("  ✅ Cliente insertado")
    except pymongo.errors.DuplicateKeyError:
        print("  ℹ️ Cliente de ejemplo ya existía")

    producto_ejemplo = {
        "sku": "PROD001",
        "nombre": "Laptop Dell XPS 15",
        "categoria": "Electrónica",
        "precio_unitario": 4500000,
        "stock": 25,
        "proveedor": "Dell Colombia S.A.S",
        "fecha_creacion": datetime.now()
    }
    try:
        db.productos.insert_one(producto_ejemplo)
        print("  ✅ Producto insertado")
    except pymongo.errors.DuplicateKeyError:
        print("  ℹ️ Producto de ejemplo ya existía")

    cliente_id = db.clientes.find_one({"codigo_cliente": "CLI001"})["_id"]
    prod_id = db.productos.find_one({"sku": "PROD001"})["_id"]

    venta_ejemplo = {
        "numero_factura": "FAC-2026-0001",
        "cliente_id": cliente_id,
        "fecha_venta": datetime.now(),
        "items": [
            {
                "producto_id": prod_id,
                "cantidad": 1,
                "precio_unitario": 4500000,
                "subtotal": 4500000
            }
        ],
        "total": 4500000,
        "metodo_pago": "Tarjeta de Crédito",
        "estado": "Completada"
    }
    db.ventas.insert_one(venta_ejemplo)
    print("  ✅ Venta insertada")

    # 4. Crear colección OLAP (Analítica)
    print("\n📊 Creando colección analítica (OLAP)...")
    if "ventas_analiticas" not in db.list_collection_names():
        db.create_collection("ventas_analiticas")
    print("  ✅ Colección 'ventas_analiticas' creada")

    print("\n✅ Estructura de ventas creada exitosamente en Atlas!")
    print("🔍 Abre MongoDB Compass para ver las colecciones creadas.")

    client.close()


if __name__ == "__main__":
    crear_estructura_ventas()
