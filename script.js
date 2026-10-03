// Catálogo de Productos del E-Commerce (Ventas MongoDB Atlas)
const productosCatalog = [
  { sku: "PROD001", nombre: "Laptop Dell XPS 15", categoria: "Electrónica", precio: 4500000 },
  { sku: "PROD002", nombre: "Audífonos Sony WH-1000XM5", categoria: "Audio", precio: 1200000 },
  { sku: "PROD003", nombre: "Monitor Samsung 4K 27\"", categoria: "Monitores", precio: 1650000 },
  { sku: "PROD004", nombre: "Teclado Mecánico RGB", categoria: "Accesorios", precio: 350000 },
  { sku: "PROD005", nombre: "Mouse Ergonómico Inalámbrico", categoria: "Accesorios", precio: 180000 },
  { sku: "PROD006", nombre: "Silla Ergonómica Pro", categoria: "Muebles", precio: 850000 }
];

// Estado global de la aplicación
let wishlist = [];
let currentRolloutPercentage = 10; // Por defecto: 10% (Ticket 2 - Canary)

// Evaluar si el usuario tiene acceso a la Wishlist según el Feature Flag
function isWishlistEnabled() {
  if (currentRolloutPercentage === 0) return false;
  if (currentRolloutPercentage === 100) return true;
  // Simulación para el 10% de rollout (ej. clientes con ID terminado en 1)
  return true; 
}

// Cambiar porcentaje de Feature Flag en tiempo real
function cambiarRollout(percentage) {
  currentRolloutPercentage = parseInt(percentage);
  const badge = document.getElementById("flagStatusBadge");
  
  if (currentRolloutPercentage === 0) {
    badge.innerText = "Estado: 0% Rollout (OFF / Oculto)";
    badge.style.background = "#fee2e2";
    badge.style.color = "#991b1b";
  } else if (currentRolloutPercentage === 10) {
    badge.innerText = "Estado: 10% Rollout (Canary / Beta)";
    badge.style.background = "#fef3c7";
    badge.style.color = "#92400e";
  } else {
    badge.innerText = "Estado: 100% Rollout (ON / General)";
    badge.style.background = "#dcfce7";
    badge.style.color = "#166534";
  }

  renderApp();
}

// Renderizar la tienda y visibilidad de Wishlist
function renderApp() {
  const isEnabled = isWishlistEnabled();
  
  // 1. Mostrar u ocultar botón de cabecera
  const btnHeader = document.getElementById("btnHeaderWishlist");
  if (btnHeader) {
    btnHeader.style.display = isEnabled ? "inline-block" : "none";
  }

  // 2. Renderizar productos
  const grid = document.getElementById("productsGrid");
  if (!grid) return;
  grid.innerHTML = "";

  productosCatalog.forEach(p => {
    const isSaved = wishlist.some(item => item.sku === p.sku);
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div>
        <span class="product-category">${p.categoria}</span>
        <h4 class="product-title">${p.nombre}</h4>
        <div class="product-sku">SKU: ${p.sku}</div>
        <div class="product-price">$${p.precio.toLocaleString("es-CO")}</div>
      </div>
      <div class="product-actions">
        <button class="btn-buy" onclick="comprar('${p.sku}')">Comprar</button>
        ${isEnabled ? `
          <button class="btn-wishlist-card" onclick="toggleDeseo('${p.sku}')">
            ${isSaved ? "❤️ Guardado" : "🤍 Guardar"}
          </button>
        ` : ""}
      </div>
    `;
    grid.appendChild(card);
  });

  // 3. Actualizar contador
  const countBadge = document.getElementById("wishlistCount");
  const modalCount = document.getElementById("modalWishlistCount");
  if (countBadge) countBadge.innerText = wishlist.length;
  if (modalCount) modalCount.innerText = wishlist.length;
}

// Agregar o quitar de la lista de deseos
function toggleDeseo(sku) {
  const prod = productosCatalog.find(p => p.sku === sku);
  if (!prod) return;

  const index = wishlist.findIndex(item => item.sku === sku);
  if (index > -1) {
    wishlist.splice(index, 1);
  } else {
    wishlist.push({ ...prod, fecha: new Date().toLocaleTimeString() });
  }

  renderApp();
  renderModalItems();
}

function comprar(sku) {
  const prod = productosCatalog.find(p => p.sku === sku);
  alert(`¡Compra iniciada para: ${prod ? prod.nombre : sku}!`);
}

// Modal de Wishlist (Ticket 3)
function abrirModalWishlist() {
  if (!isWishlistEnabled()) return;
  renderModalItems();
  document.getElementById("wishlistModal").style.display = "flex";
}

function cerrarModalWishlist() {
  document.getElementById("wishlistModal").style.display = "none";
}

function renderModalItems() {
  const container = document.getElementById("wishlistItemsContainer");
  if (!container) return;

  if (wishlist.length === 0) {
    container.innerHTML = `<div class="wishlist-empty">Tu lista de deseos está vacía. ¡Guarda tus productos favoritos!</div>`;
    return;
  }

  container.innerHTML = wishlist.map(item => `
    <div class="wishlist-item">
      <div class="wishlist-item-info">
        <h5>${item.nombre}</h5>
        <span>${item.categoria} | $${item.precio.toLocaleString("es-CO")}</span>
      </div>
      <button class="btn-remove-wishlist" onclick="toggleDeseo('${item.sku}')">Eliminar</button>
    </div>
  `).join("");
}

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  renderApp();
});
