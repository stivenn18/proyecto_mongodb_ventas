import os
import sys
import dns.resolver
from dotenv import load_dotenv
import pymongo
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure

sys.stdout.reconfigure(encoding='utf-8')

try:
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1']
except Exception:
    pass

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")


def conectar_mongodb():
    try:
        print("📡 Intentando conectar a MongoDB Atlas...")
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ ¡Conexión exitosa a MongoDB Atlas!")
        db = client["ventas_db"]
        return client, db
    except ConnectionFailure:
        print("❌ Error: No se pudo contactar al servidor.")
    except ConfigurationError as e:
        print(f"❌ Error de configuración: {e}")
    except OperationFailure as e:
        print(f"❌ Error de autenticación: {e}")
    return None, None


if __name__ == "__main__":
    client, db = conectar_mongodb()
    if client:
        client.close()
        print("🔒 Conexión cerrada.")

# prueba de branch protection