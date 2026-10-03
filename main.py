from wishlist import WishlistService


def iniciar_aplicacion_ventas():
    print("🛍️ Iniciando Sistema de Ventas & Wishlist E-Commerce...")
    # Por defecto, en Trunk-Based Development el flag inicia en True/False según el ambiente
    service = WishlistService(feature_flag_enabled=True)
    print("✅ WishlistService inicializado correctamente.")
    return service


if __name__ == "__main__":
    iniciar_aplicacion_ventas()
