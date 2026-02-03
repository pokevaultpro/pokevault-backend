const token = localStorage.getItem("token");
if (!token) window.location.href = "index.html";

let shoppingList = [];     // cart items
let products = [];         // full products
let supermarkets = [];     // full supermarkets

const BASE_URL = "http://localhost:8000";

const totalAllEl = document.getElementById("total-all");
const totalPendingEl = document.getElementById("total-pending");

// =========================
// 1. LOAD DATA FROM BACKEND
// =========================

async function loadCart() {
  const res = await apiFetch(`${BASE_URL}/cart`, {
    headers: { "Authorization": "Bearer " + token }
  });
  return res.ok ? res.json() : [];
}

async function loadProducts() {
  const res = await apiFetch(`${BASE_URL}/product`);
  return res.ok ? res.json() : [];
}

async function loadSupermarkets() {
  const res = await apiFetch(`${BASE_URL}/supermarket`);
  return res.ok ? res.json() : [];
}


// =========================
// 2. INIT PAGE
// =========================

async function initCart() {
  // Load all data
  products = await loadProducts();
  supermarkets = await loadSupermarkets();
  const rawCart = await loadCart();

  // JOIN manuale cart → product → supermarket
  shoppingList = rawCart.map(item => {
    const product = products.find(p => p.id === item.product_id);
    const supermarket = supermarkets.find(s => s.id === product.supermarket_id);

    return {
      ...item,
      product,
      supermarket
    };
  });

  renderList();
  populateStoreFilter();
}

initCart();


// =========================
// 3. RENDER LIST
// =========================

function renderList() {
  const listEl = document.getElementById("shopping-list");
  const boughtEl = document.getElementById("shopping-bought");

  listEl.innerHTML = "";
  boughtEl.innerHTML = "";

  const storeFilter = document.getElementById("filter-store").value;

  // =========================
  // 1. FILTRO PER NEGOZIO
  // =========================
  let filtered = shoppingList.filter(item => {
    return storeFilter === "all" || item.supermarket.name === storeFilter;
  });

  // =========================
  // 2. SPLIT PENDING / BOUGHT
  // =========================
  let pendingItems = filtered.filter(i => !i.checked);
  let boughtItems = filtered.filter(i => i.checked);

  // =========================
  // 3. ORDINAMENTO
  // =========================
  if (storeFilter === "all") {
    // Ordina per nome
    pendingItems.sort((a, b) => a.product.name.localeCompare(b.product.name));
    boughtItems.sort((a, b) => a.product.name.localeCompare(b.product.name));
  } else {
    // Ordina per aisle_order
    pendingItems.sort((a, b) => {
      const aOrder = a.product.aisle_order ?? 9999;
      const bOrder = b.product.aisle_order ?? 9999;
      return aOrder - bOrder;
    });

    boughtItems.sort((a, b) => {
      const aOrder = a.product.aisle_order ?? 9999;
      const bOrder = b.product.aisle_order ?? 9999;
      return aOrder - bOrder;
    });
  }

  // =========================
  // 4. RENDER
  // =========================
  [...pendingItems, ...boughtItems].forEach(item => {
    const product = item.product;
    const supermarket = item.supermarket;

    const price = product.discounted_price ?? product.original_price;
    const subtotal = (price * item.quantity).toFixed(2);
    const hasDiscount = product.discounted_price !== null;

    const div = document.createElement("div");
    div.className = "shopping-item" + (item.checked ? " bought" : "");

    div.onclick = () => openProductModal(
      {
        ...product,
        quantity: item.quantity,
        store: supermarket.name,
        location: product.location,
        nutritional: product.nutritional
      },
      supermarket
    );

    div.innerHTML = `
      <div class="check-circle" onclick="toggleBought(event, ${item.id})">
        ${item.checked ? "✔" : ""}
      </div>

      <img src="${BASE_URL + product.image}" class="item-img ${item.checked ? "bought-img" : ""}">

      <div class="item-info">
        <div class="name ${item.checked ? "bought-text" : ""}">
          ${product.name}
          ${hasDiscount ? `<span class="sale-badge">SALE</span>` : ""}
        </div>

        <div class="unit-line">
          <span class="unit-price ${hasDiscount ? "discounted-unit" : ""}">
            ${price.toFixed(2).replace('.', ',')} € / pz
          </span>

          <span class="store-tag">${supermarket.name}</span>
        </div>
      </div>

      <div class="item-right">
        <div class="qty-box">
          <button class="qty-btn" onclick="handleQtyClick(event, ${item.id}, -1)">−</button>
          <span>${item.quantity}</span>
          <button class="qty-btn" onclick="handleQtyClick(event, ${item.id}, 1)">+</button>
        </div>

        <span class="price ${item.checked ? "bought-price" : ""} ${hasDiscount ? "discounted" : ""}">
          € ${subtotal.replace('.', ',')}
        </span>

        <button class="remove-btn" onclick="handleRemoveClick(event, ${item.id})">
          <img src="${BASE_URL}/static/icons/trash.svg" class="trash-icon">
        </button>
      </div>
    `;

    if (item.checked) boughtEl.appendChild(div);
    else listEl.appendChild(div);
  });

  updateTotals();
  updateSectionVisibility();
}



// =========================
// 4. SECTION VISIBILITY
// =========================

function updateSectionVisibility() {
  document.getElementById("label-pending").style.display =
    shoppingList.some(i => !i.checked) ? "block" : "none";

  document.getElementById("shopping-list").style.display =
    shoppingList.some(i => !i.checked) ? "block" : "none";

  document.getElementById("label-bought").style.display =
    shoppingList.some(i => i.checked) ? "block" : "none";

  document.getElementById("shopping-bought").style.display =
    shoppingList.some(i => i.checked) ? "block" : "none";
}


// =========================
// 5. QUANTITY
// =========================

async function handleQtyClick(event, id, delta) {
  event.stopPropagation();
  await updateQty(id, delta);
}

async function updateQty(id, delta) {
  const item = shoppingList.find(i => i.id === id);
  if (!item) return;

  const newQty = Math.max(1, item.quantity + delta);

  await apiFetch(`${BASE_URL}/cart/${id}`, {
    method: "PUT",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ quantity: newQty })
  });

  item.quantity = newQty;
  renderList();
}


// =========================
// 6. REMOVE ITEM
// =========================

async function handleRemoveClick(event, id) {
  event.stopPropagation();
  await removeItem(id);
}

async function removeItem(id) {
  await apiFetch(`${BASE_URL}/cart/${id}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + token }
  });

  shoppingList = shoppingList.filter(i => i.id !== id);
  renderList();
  populateStoreFilter();
}


// =========================
// 7. CHECKED / UNCHECKED
// =========================

async function toggleBought(event, id) {
  event.stopPropagation();

  const item = shoppingList.find(i => i.id === id);
  if (!item) return;

  const newValue = !item.checked;

  await apiFetch(`${BASE_URL}/cart/${id}`, {
    method: "PUT",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ checked: newValue })
  });

  item.checked = newValue;
  renderList();
}


// =========================
// 8. TOTALS
// =========================

function updateTotals() {
  const storeFilter = document.getElementById("filter-store").value;

  const filtered = shoppingList.filter(item => {
    const store = item.supermarket.name;
    return storeFilter === "all" || store === storeFilter;
  });

  const total = filtered.reduce((acc, i) => {
    const price = i.product.discounted_price ?? i.product.original_price;
    return acc + price * i.quantity;
  }, 0);

  const pending = filtered
    .filter(i => !i.checked)
    .reduce((acc, i) => {
      const price = i.product.discounted_price ?? i.product.original_price;
      return acc + price * i.quantity;
    }, 0);

  totalAllEl.textContent = total.toFixed(2).replace('.', ',') + " €";
  totalPendingEl.textContent = pending.toFixed(2).replace('.', ',') + " €";
}


// =========================
// 9. STORE FILTER
// =========================

function populateStoreFilter() {
  const storeSelect = document.getElementById("filter-store");
  const currentValue = storeSelect.value;

  const stores = [...new Set(shoppingList.map(i => i.supermarket.name))];

  storeSelect.innerHTML = `<option value="all">Tutti i negozi</option>`;

  stores.forEach(store => {
    storeSelect.innerHTML += `<option value="${store}">${store}</option>`;
  });

  if ([...storeSelect.options].some(opt => opt.value === currentValue)) {
    storeSelect.value = currentValue;
  } else {
    storeSelect.value = "all";
  }
}


// =========================
// 10. CLEAR CART
// =========================

async function clearCart() {
  if (!confirm("Vuoi davvero svuotare tutto il carrello?")) return;

  await apiFetch(`${BASE_URL}/cart`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + token }
  });

  shoppingList = [];
  renderList();
  populateStoreFilter();
  updateTotals();
}
