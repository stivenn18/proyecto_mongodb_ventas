import os
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from wishlist import WishlistService

load_dotenv()

app = FastAPI(
    title="Sistema de Ventas & Wishlist E-Commerce API",
    description="API con soporte de Auto-deploy a Render, Health Check y Feature Toggles con ConfigCat",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de ConfigCat SDK (o modo fallback local si no hay SDK Key configurada)
CONFIGCAT_SDK_KEY = os.getenv("CONFIGCAT_SDK_KEY")
configcat_client = None

if CONFIGCAT_SDK_KEY:
    try:
        import configcatclient
        configcat_client = configcatclient.get(CONFIGCAT_SDK_KEY)
        print("✅ ConfigCat SDK conectado exitosamente a la nube.")
    except Exception as e:
        print(f"⚠️ Error conectando ConfigCat SDK: {e}. Usando modo local.")
else:
    print("ℹ️ CONFIGCAT_SDK_KEY no configurada. Operando en modo de Feature Toggle local.")

# Servicio de Wishlist
wishlist_service = WishlistService(feature_flag_enabled=True)


def is_feature_enabled(flag_key: str, default_val: bool = True) -> bool:
    """Evalúa el estado del Feature Flag en ConfigCat o fallback local"""
    if configcat_client:
        try:
            return configcat_client.get_value(flag_key, default_val)
        except Exception:
            return default_val
    return default_val


class ProductItem(BaseModel):
    sku: str
    nombre: str
    precio_unitario: float
    categoria: str = "General"


class AddWishlistRequest(BaseModel):
    cliente_id: str
    producto: ProductItem


@app.get("/")
def get_index():
    """Servir la interfaz gráfica de la tienda e-commerce"""
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"mensaje": "API de Ventas & Wishlist en ejecución en Render"}


@app.get("/style.css")
def get_style():
    """Servir la hoja de estilos CSS"""
    style_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(style_path):
        return FileResponse(style_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/script.js")
def get_script():
    """Servir el archivo JavaScript con la lógica y ConfigCat SDK"""
    script_path = os.path.join(os.path.dirname(__file__), "script.js")
    if os.path.exists(script_path):
        return FileResponse(script_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")


@app.get("/health")
def health_check():
    """Endpoint de Health Check para Auto-deploy y monitoreo en Render"""
    return {
        "status": "healthy",
        "service": "ventas-wishlist-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "features": {
            "wishlist_enabled": is_feature_enabled("wishlist_enabled", True),
            "pagos_express_v1": is_feature_enabled("pagos-express-v1", False)
        }
    }


@app.get("/api/flags")
def get_feature_flags():
    """Consulta el estado en vivo de los Feature Flags"""
    return {
        "wishlist_enabled": is_feature_enabled("wishlist_enabled", True),
        "pagos_express_v1": is_feature_enabled("pagos-express-v1", False),
        "source": "ConfigCat Cloud" if configcat_client else "Local Default"
    }


class PagoExpressRequest(BaseModel):
    cliente_id: str
    sku: str
    monto: float


@app.post("/api/pagos-express")
def procesar_pago_express(req: PagoExpressRequest):
    """Caso Taller 6: Endpoint protegido por el Feature Toggle 'pagos-express-v1'"""
    flag_active = is_feature_enabled("pagos-express-v1", False)
    if not flag_active:
        raise HTTPException(
            status_code=403,
            detail="La funcionalidad de Pagos Express (1-clic) está deshabilitada (Toggle 'pagos-express-v1' en OFF al 0%)."
        )
    return {
        "status": "success",
        "metodo": "pagos_express_1_click",
        "transaccion_id": f"TX-EXP-{abs(hash(req.cliente_id + req.sku)) % 1000000:06d}",
        "cliente_id": req.cliente_id,
        "sku": req.sku,
        "monto": req.monto,
        "tiempo_respuesta_ms": 35,
        "mensaje": "Pago procesado instantáneamente mediante flujo protegido por Feature Toggle."
    }


@app.post("/api/wishlist")
def agregar_a_wishlist(req: AddWishlistRequest):
    """Ticket 1 & 2: Agregar producto a la lista de deseos con Feature Flag"""
    flag_active = is_feature_enabled("wishlist_enabled", True)
    wishlist_service.feature_flag_enabled = flag_active

    if not flag_active:
        raise HTTPException(status_code=403, detail="La funcionalidad de lista de deseos está deshabilitada (Toggle OFF).")

    res = wishlist_service.agregar_producto_deseo(req.cliente_id, req.producto.model_dump())
    return res


@app.get("/api/wishlist/{cliente_id}")
def obtener_wishlist_cliente(cliente_id: str) -> List[Dict[str, Any]]:
    """Ticket 3: Consultar lista de deseos completa"""
    flag_active = is_feature_enabled("wishlist_enabled", True)
    wishlist_service.feature_flag_enabled = flag_active

    if not flag_active:
        return []
    return wishlist_service.obtener_deseos(cliente_id)


@app.delete("/api/wishlist/{cliente_id}/{sku}")
def eliminar_de_wishlist(cliente_id: str, sku: str):
    """Ticket 3: Eliminar producto de la lista de deseos"""
    flag_active = is_feature_enabled("wishlist_enabled", True)
    wishlist_service.feature_flag_enabled = flag_active

    if not flag_active:
        raise HTTPException(status_code=403, detail="Funcionalidad deshabilitada.")

    ok = wishlist_service.eliminar_deseo(cliente_id, sku)
    return {"status": "success" if ok else "not_found", "sku": sku}
