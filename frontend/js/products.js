import CONFIG from "./config.js";
import { openProductModal } from "./modal-function.js";


let allProducts = [];
let supermarkets = [];
let currentCategory = "all";
let currentStore = "all";
const params = new URLSearchParams(window.location.search);
if (params.get("sale") === "1") {
  currentCategory = "sale";

  // attiva la pillola "Offerte"
  document.querySelectorAll(".cat-pill").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.cat === "sale");
  });
}

async function loadProducts() {
  const [prodRes, supRes] = await Promise.all([
    apiFetch(`${CONFIG.API_BASE_URL}/product`),
    apiFetch(`${CONFIG.API_BASE_URL}/supermarket`)
  ]);

  allProducts = prodRes.ok ? await prodRes.json() : [];
  supermarkets = supRes.ok ? await supRes.json() : [];

  populateStoreFilter();


  renderProducts();
}


loadProducts();

document.getElementById("search-input")
  .addEventListener("input", renderProducts);
document.getElementById("store-filter")
  .addEventListener("change", setStoreFilter);
document.querySelectorAll(".cat-pill").forEach(btn => {
  btn.addEventListener("click", () => {
    const cat = btn.dataset.cat;
    setCategory(cat);
  });
});



function setCategory(cat) {
  currentCategory = cat;

  document.querySelectorAll(".cat-pill").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.cat === cat);
  });

  renderProducts();
}

function renderProducts() {
  const grid = document.getElementById("products-grid");
  const search = document.getElementById("search-input").value.toLowerCase();

  grid.innerHTML = "";

  const filtered = allProducts.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search);

    const matchesCategory =
      currentCategory === "all" ||
      (currentCategory === "sale" && p.discounted_price !== null) ||
      p.category === currentCategory;

     const matchesStore =
  currentStore === "all" ||
  p.supermarket_id == currentStore;


    return matchesSearch && matchesCategory && matchesStore;
  });
    // ORDINAMENTO
    if (currentStore === "all") {
      // Ordina per nome
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else {
      // Ordina per aisle_order (se manca, metti in fondo)
      filtered.sort((a, b) => {
        const aOrder = a.aisle_order ?? 9999;
        const bOrder = b.aisle_order ?? 9999;
        return aOrder - bOrder;
      });
    }



  filtered.forEach(p => {
    const hasDiscount = p.discounted_price !== null;
    const price = hasDiscount ? p.discounted_price : p.original_price;

      const supermarket = supermarkets.find(s => s.id === p.supermarket_id);
    const supermarketName = supermarket ? supermarket.name : "";

    const card = document.createElement("div");
    card.className = "product-card";
    card.addEventListener("click", () => {
  openProductModal(p, supermarket);
});


card.innerHTML = `
  <div class="img-wrapper">
    <img src="${p.image}" class="product-img">
  </div>

  <div class="product-info">

    <div class="product-name">${p.name}</div>

    <div class="product-supermarket-tag">
      ${supermarket ? supermarket.name : ""}
    </div>

    ${
      hasDiscount
        ? `
          <div class="price-row">
            <span class="old-price">€ ${p.original_price.toFixed(2).replace(".", ",")}</span>
            <span class="new-price">€ ${p.discounted_price.toFixed(2).replace(".", ",")}</span>
            <span class="discount-tag">-${Math.round((1 - p.discounted_price / p.original_price) * 100)}%</span>
          </div>
        `
        : `
          <div class="price-row">
            <span class="regular-price">€ ${p.original_price.toFixed(2).replace(".", ",")}</span>
          </div>
        `
    }

    <button class="add-btn" data-id="${p.id}">
      + Lista Spesa
    </button>


  </div>
`;

card.querySelector(".add-btn").addEventListener("click", (event) => {
  event.stopPropagation(); // evita apertura modal
  addToCart(p.id);
});

card.addEventListener("click", () => {
  openProductModal(p, supermarket);
});




    grid.appendChild(card);
  });
}

async function addToCart(productId) {
  const res = await apiFetch(`${CONFIG.API_BASE_URL}/cart`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token"),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ product_id: productId, quantity: 1 })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    showToast(err.detail || "Errore durante l'aggiunta", false);
    return;
  }

  showToast("Aggiunto alla lista spesa");
}


function showToast(message, success = true) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.background = success ? "#2ecc71" : "#e53935";
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
}

function populateStoreFilter() {
  const select = document.getElementById("store-filter");
  select.innerHTML = `<option value="all">Tutti i negozi</option>`;

  supermarkets.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    select.appendChild(opt);
  });
}
function setStoreFilter() {
  currentStore = document.getElementById("store-filter").value;
  renderProducts();
}
