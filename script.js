// Clave Real de ConfigCat SDK
const CONFIGCAT_SDK_KEY = "configcat-sdk-1/jyHfCAeT0E2Arwo28sVn6g/4yptu_1D2UORDKiU3dUviw";
const FLAG_KEY = "wishlist_enabled";

// Catálogo Oficial de Productos
const productosCatalog = [
  { sku: "PROD001", nombre: "Laptop Dell XPS 15 Intel i7", categoria: "Electrónica", precio: 4500000, stock: 25, icono: "fa-laptop" },
  { sku: "PROD002", nombre: "Audífonos Sony WH-1000XM5 Noise Cancelling", categoria: "Audio", precio: 1200000, stock: 40, icono: "fa-headphones" },
  { sku: "PROD003", nombre: "Monitor Samsung 4K UHD 27\"", categoria: "Monitores", precio: 1650000, stock: 15, icono: "fa-desktop" },
  { sku: "PROD004", nombre: "Teclado Mecánico RGB Switch Red", categoria: "Accesorios", precio: 350000, stock: 80, icono: "fa-keyboard" },
  { sku: "PROD005", nombre: "Mouse Ergonómico Inalámbrico MX Master 3S", categoria: "Accesorios", precio: 420000, stock: 55, icono: "fa-computer-mouse" },
  { sku: "PROD006", nombre: "Silla Ergonómica Pro Soporte Lumbar", categoria: "Muebles", precio: 850000, stock: 12, icono: "fa-chair" }
];

// Estado de la aplicación
let wishlist = [];
let currentCategory = "Todas";
let searchQuery = "";
let flagState = false; // Estado del Feature Flag (wishlist_enabled)
let pagosExpressState = false; // Estado del Feature Flag (pagos-express-v1)
let simulationMode = "cloud"; // "cloud" | "manual_off" | "manual_on"
let configcatClient = null;

// 1. Inicialización de ConfigCat SDK
function initConfigCat() {
  const badge = document.getElementById("cloudFlagBadge");
  badge.innerText = "Conectando...";
  badge.className = "status-badge";

  try {
    if (window.configcat) {
      configcatClient = window.configcat.getClient(
        CONFIGCAT_SDK_KEY,
        window.configcat.PollingMode.AutoPoll,
        { pollIntervalSeconds: 5 } // Polling en tiempo real cada 5 segundos
      );

      configcatClient.on('clientReady', async () => {
        console.log("✅ ConfigCat JS SDK Listo");
        evaluarFlagDesdeCloud();
      });

      configcatClient.on('configChanged', () => {
        console.log("⚡ ConfigCat: Configuración de Feature Flag cambiada en la nube");
        evaluarFlagDesdeCloud();
      });
    } else {
      console.warn("ConfigCat SDK JS no disponible, usando API del backend");
      consultarFlagBackend();
    }
  } catch (err) {
    console.error("Error inicializando ConfigCat:", err);
    consultarFlagBackend();
  }
}

async function evaluarFlagDesdeCloud() {
  if (simulationMode !== "cloud") return;

  if (configcatClient) {
    const value = await configcatClient.getValueAsync(FLAG_KEY, false);
    actualizarEstadoFlag(value, "ConfigCat Cloud");
  } else {
    consultarFlagBackend();
  }
}

async function consultarFlagBackend() {
  try {
    const res = await fetch("/api/flags");
    if (res.ok) {
      const data = await res.json();
      actualizarEstadoFlag(data.wishlist_enabled, data.source);
    }
  } catch (e) {
    // Si corre como archivo estático local sin backend
    actualizarEstadoFlag(false, "Local Default (OFF)");
  }
}

function forzarSincronizacionCloud() {
  showToast("🔄 Sincronizando con ConfigCat Cloud...", "info");
  if (configcatClient) {
    configcatClient.forceRefreshAsync().then(() => {
      evaluarFlagDesdeCloud();
      showToast("✅ Sincronización completada.", "success");
    });
  } else {
    consultarFlagBackend();
  }
}

function actualizarEstadoFlag(enabled, source) {
  flagState = enabled;
  const badge = document.getElementById("cloudFlagBadge");
  const indicator = document.getElementById("flagModeIndicator");

  if (badge) {
    badge.innerText = flagState ? "ON (Habilitado)" : "OFF (Deshabilitado)";
    badge.className = `status-badge ${flagState ? "on" : "off"}`;
  }

  if (indicator) {
    indicator.innerHTML = `<i class="fa-solid fa-${flagState ? "circle-check" : "circle-xmark"}"></i> Estado: <strong>${flagState ? "100% / Activo" : "0% / Oculto"}</strong> (${source})`;
  }

  renderApp();
}

// 2. Modos de Simulación para Demostración en Vivo
function aplicarSimulacionManual(valor) {
  simulationMode = valor ? "manual_on" : "manual_off";
  actualizarBotonesSegmented();
  actualizarEstadoFlag(valor, "Simulación Manual");
  showToast(`Modo cambiado: Feature Flag forzado a ${valor ? "ON (100%)" : "OFF (0%)"}`, valor ? "success" : "warning");
}

function usarConfigCatCloud() {
  simulationMode = "cloud";
  actualizarBotonesSegmented();
  showToast("Conectando con ConfigCat Cloud...", "info");
  evaluarFlagDesdeCloud();
}

function actualizarBotonesSegmented() {
  document.getElementById("segBtnOff").className = `seg-btn ${simulationMode === "manual_off" ? "active" : ""}`;
  document.getElementById("segBtnCloud").className = `seg-btn ${simulationMode === "cloud" ? "active" : ""}`;
  document.getElementById("segBtnOn").className = `seg-btn ${simulationMode === "manual_on" ? "active" : ""}`;
}

// 3. Renderizado de la Tienda
function renderApp() {
  // Visibilidad del botón de cabecera
  const btnHeader = document.getElementById("btnHeaderWishlist");
  if (btnHeader) {
    btnHeader.style.display = flagState ? "flex" : "none";
  }

  // Filtrado de productos
  const grid = document.getElementById("productsGrid");
  if (!grid) return;
  grid.innerHTML = "";

  const filtrados = productosCatalog.filter(p => {
    const matchCat = currentCategory === "Todas" || p.categoria === currentCategory;
    const matchSearch = p.nombre.toLowerCase().includes(searchQuery.toLowerCase()) || p.sku.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  if (filtrados.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No se encontraron productos coincidentes.</div>`;
    return;
  }

  filtrados.forEach(p => {
    const isSaved = wishlist.some(item => item.sku === p.sku);
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-img-wrapper">
        <span class="product-tag">${p.categoria}</span>
        <i class="fa-solid ${p.icono}"></i>
      </div>
      <div class="product-body">
        <div>
          <span class="product-category">${p.categoria}</span>
          <h4 class="product-title">${p.nombre}</h4>
          <div class="product-sku">SKU: ${p.sku}</div>
        </div>
        <div>
          <div class="product-price-row">
            <div class="product-price">$${p.precio.toLocaleString("es-CO")}</div>
            <div class="product-stock"><i class="fa-solid fa-check"></i> Stock: ${p.stock}</div>
          </div>
          <div class="product-actions">
            <button class="btn-buy" onclick="comprar('${p.sku}')">
              <i class="fa-solid fa-bag-shopping"></i> Comprar
            </button>
            <button class="btn-express ${pagosExpressState ? 'active' : 'locked'}" onclick="procesarPagoExpressClick('${p.sku}', ${p.precio})" title="${pagosExpressState ? 'Pago Express 1-Clic activo' : 'Toggle pagos-express-v1 apagado (0%)'}">
              <i class="fa-solid ${pagosExpressState ? 'fa-bolt' : 'fa-lock'}"></i> 1-Clic
            </button>
            ${flagState ? `
              <button class="btn-wishlist-card ${isSaved ? "saved" : ""}" onclick="toggleDeseo('${p.sku}')">
                <i class="fa-${isSaved ? "solid" : "regular"} fa-heart"></i>
                <span>${isSaved ? "Guardado" : "Deseo"}</span>
              </button>
            ` : ""}
          </div>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });

  // Actualizar contadores
  const countBadge = document.getElementById("wishlistCount");
  const modalCount = document.getElementById("modalWishlistCount");
  if (countBadge) countBadge.innerText = wishlist.length;
  if (modalCount) modalCount.innerText = `${wishlist.length} producto${wishlist.length === 1 ? "" : "s"}`;
}

// 4. Lógica de Wishlist (Ticket 1, 2 y 3)
function toggleDeseo(sku) {
  if (!flagState) {
    showToast("⚠️ La función de Lista de Deseos está deshabilitada (Toggle OFF).", "warning");
    return;
  }

  const prod = productosCatalog.find(p => p.sku === sku);
  if (!prod) return;

  const index = wishlist.findIndex(item => item.sku === sku);
  if (index > -1) {
    wishlist.splice(index, 1);
    showToast(`Eliminado de lista de deseos: ${prod.nombre}`, "warning");
  } else {
    wishlist.push({ ...prod, fechaAgregado: new Date().toLocaleTimeString() });
    showToast(`❤️ Guardado en tu lista de deseos: ${prod.nombre}`, "success");
  }

  renderApp();
  renderModalItems();
}

function filtrarCategoria(categoria, elem) {
  currentCategory = categoria;
  document.querySelectorAll(".cat-pill").forEach(p => p.classList.remove("active"));
  if (elem) elem.classList.add("active");
  renderApp();
}

function filtrarProductos() {
  searchQuery = document.getElementById("searchInput").value;
  renderApp();
}

function comprar(sku) {
  const prod = productosCatalog.find(p => p.sku === sku);
  showToast(`🛍️ Procesando orden para: ${prod ? prod.nombre : sku}...`, "info");
}

// 5. Modal de Wishlist
function abrirModalWishlist() {
  if (!flagState) return;
  renderModalItems();
  document.getElementById("wishlistModal").style.display = "flex";
}

function cerrarModalWishlist() {
  document.getElementById("wishlistModal").style.display = "none";
}

function cerrarModalFuera(e) {
  if (e.target.id === "wishlistModal") {
    cerrarModalWishlist();
  }
}

function renderModalItems() {
  const container = document.getElementById("wishlistItemsContainer");
  const totalAmountElem = document.getElementById("totalWishlistAmount");
  if (!container) return;

  if (wishlist.length === 0) {
    container.innerHTML = `
      <div class="wishlist-empty">
        <i class="fa-regular fa-heart"></i>
        <h4>Tu lista de deseos está vacía</h4>
        <p>Haz clic en el botón de corazón en los productos para guardarlos aquí.</p>
      </div>
    `;
    if (totalAmountElem) totalAmountElem.innerText = "$0";
    return;
  }

  let total = 0;
  container.innerHTML = wishlist.map(item => {
    total += item.precio;
    return `
      <div class="wishlist-item">
        <div class="wishlist-item-info">
          <h5>${item.nombre}</h5>
          <span>SKU: ${item.sku} &middot; $${item.precio.toLocaleString("es-CO")}</span>
        </div>
        <button class="btn-remove-wishlist" onclick="toggleDeseo('${item.sku}')">
          <i class="fa-solid fa-trash"></i> Quitar
        </button>
      </div>
    `;
  }).join("");

  if (totalAmountElem) {
    totalAmountElem.innerText = `$${total.toLocaleString("es-CO")}`;
  }
}

function comprarWishlistCompleta() {
  if (wishlist.length === 0) return;
  showToast(`🎉 ¡Compra exitosa de ${wishlist.length} productos guardados!`, "success");
  wishlist = [];
  cerrarModalWishlist();
  renderApp();
}

// 6. Toasts de Notificación
function showToast(mensaje, tipo = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  const icon = tipo === "success" ? "fa-circle-check" : (tipo === "warning" ? "fa-triangle-exclamation" : "fa-circle-info");
  const iconColor = tipo === "success" ? "#4ade80" : (tipo === "warning" ? "#fbbf24" : "#60a5fa");

  toast.innerHTML = `<i class="fa-solid ${icon}" style="color: ${iconColor};"></i> <span>${mensaje}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// 7. Lógica de Compra Express (1-Clic)
function cambiarPagosExpress(enabled) {
  pagosExpressState = enabled;
  const badge = document.getElementById("cloudPagosBadge");
  const btnOff = document.getElementById("segPagosOff");
  const btnOn = document.getElementById("segPagosOn");

  if (badge) {
    badge.innerText = enabled ? "ON (Habilitado)" : "OFF (Deshabilitado)";
    badge.className = `status-badge ${enabled ? "on" : "off"}`;
  }
  if (btnOff && btnOn) {
    btnOff.classList.toggle("active", !enabled);
    btnOn.classList.toggle("active", enabled);
  }

  showToast(
    enabled
      ? "⚡ Función de Compra Rápida (1-Clic) habilitada exitosamente."
      : "🛡️ Función de Compra Rápida (1-Clic) deshabilitada.",
    enabled ? "success" : "info"
  );
  renderApp();
}

async function procesarPagoExpressClick(sku, monto) {
  const prod = productosCatalog.find(p => p.sku === sku);
  const nombre = prod ? prod.nombre : sku;

  if (!pagosExpressState) {
    showToast(
      `⛔ La opción de Compra en 1-Clic no está habilitada en este momento.`,
      "warning"
    );
    return;
  }

  try {
    const res = await fetch("/api/pagos-express", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cliente_id: "CLI001", sku: sku, monto: monto })
    });
    if (res.ok) {
      const data = await res.json();
      showToast(
        `⚡ ¡Compra en 1-Clic Aprobada! Orden ${data.transaccion_id} por $${monto.toLocaleString("es-CO")} (${data.tiempo_respuesta_ms}ms)`,
        "success"
      );
    } else {
      showToast(`⚡ ¡Compra en 1-Clic procesada para ${nombre}!`, "success");
    }
  } catch (e) {
    showToast(`⚡ ¡Compra en 1-Clic procesada para ${nombre}!`, "success");
  }
}

// Inicializar al cargar
document.addEventListener("DOMContentLoaded", () => {
  initConfigCat();
  renderApp();
});
