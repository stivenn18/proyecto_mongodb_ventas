import datetime
from typing import Any, Dict, List, Optional


class WishlistService:
    def __init__(self, db_client: Optional[Any] = None, feature_flag_enabled: bool = False):
        self.db = db_client
        self.feature_flag_enabled = feature_flag_enabled
        # Estructura en memoria para tests y fallback
        self._memory_wishlists: Dict[str, List[Dict[str, Any]]] = {}

    def agregar_producto_deseo(self, cliente_id: str, producto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ticket 1: Agrega un producto a la lista de deseos del cliente.
        Protegido por Feature Flag 'wishlist_enabled'.
        """
        if not self.feature_flag_enabled:
            return {
                "status": "disabled",
                "mensaje": "La funcionalidad de lista de deseos está deshabilitada temporalmente."
            }

        if not cliente_id or not producto or "sku" not in producto:
            raise ValueError("Datos de cliente o producto inválidos.")

        item = {
            "sku": producto.get("sku"),
            "nombre": producto.get("nombre"),
            "precio_unitario": producto.get("precio_unitario", 0),
            "categoria": producto.get("categoria", "General"),
            "fecha_guardado": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Si hay conexión a MongoDB, insertar en la colección
        if self.db is not None:
            self.db.wishlists.update_one(
                {"cliente_id": cliente_id},
                {"$addToSet": {"items": item}},
                upsert=True
            )
        else:
            if cliente_id not in self._memory_wishlists:
                self._memory_wishlists[cliente_id] = []
            # Evitar duplicados por SKU
            if not any(p["sku"] == item["sku"] for p in self._memory_wishlists[cliente_id]):
                self._memory_wishlists[cliente_id].append(item)

        return {
            "status": "success",
            "mensaje": f"Producto '{producto.get('nombre')}' agregado a la lista de deseos.",
            "item": item
        }

    def obtener_deseos(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Obtiene los productos en la lista de deseos del cliente"""
        if not self.feature_flag_enabled:
            return []

        if self.db is not None:
            doc = self.db.wishlists.find_one({"cliente_id": cliente_id})
            return doc.get("items", []) if doc else []

        return self._memory_wishlists.get(cliente_id, [])

    def eliminar_deseo(self, cliente_id: str, sku: str) -> bool:
        """Elimina un producto de la lista de deseos"""
        if not self.feature_flag_enabled:
            return False

        if self.db is not None:
            res = self.db.wishlists.update_one(
                {"cliente_id": cliente_id},
                {"$pull": {"items": {"sku": sku}}}
            )
            return res.modified_count > 0

        if cliente_id in self._memory_wishlists:
            inicial = len(self._memory_wishlists[cliente_id])
            self._memory_wishlists[cliente_id] = [
                p for p in self._memory_wishlists[cliente_id] if p["sku"] != sku
            ]
            return len(self._memory_wishlists[cliente_id]) < inicial
        return False
