import CONFIG from "./config.js";
import { openProductModal } from "./modal-function.js";


const token = localStorage.getItem("token");
if (!token) window.location.href = "index.html";
async function loadDashboard() {
  try {
    const [userRes, productsRes, recipesRes, supermarketsRes] = await Promise.all([
      apiFetch(`${CONFIG.API_BASE_URL}/user`, {
        headers: { Authorization: "Bearer " + token }
      }),
      apiFetch(`${CONFIG.API_BASE_URL}/product`, {
        headers: { Authorization: "Bearer " + token }
      }),
      apiFetch(`${CONFIG.API_BASE_URL}/recipe?owner_id=1`, {
        headers: { Authorization: "Bearer " + token }
      }),
       apiFetch(`${CONFIG.API_BASE_URL}/supermarket`, {
        headers: { Authorization: "Bearer " + token }
        })
    ]);

    const user = await userRes.json();
    const products = await productsRes.json();
    const recipes = await recipesRes.json();
    const supermarkets = await supermarketsRes.json();
    window.__allProducts = products;
window.__allSupermarkets = supermarkets;


    renderUser(user);
    renderOffers(products, supermarkets);
    renderDashboardQuickActions()
    renderRecipe(recipes);

  } catch (err) {
    console.error(err);
  }
}

function renderUser(user) {
  document.getElementById("user-greeting").textContent = `Ciao, ${user.first_name}! 👋`;
  document.getElementById("user-avatar").textContent = user.first_name[0];
}

function renderDashboardQuickActions() {
  const actions = [
    {
      id: "list",
      label: "Lista Spesa",
      color: "green",
      icon: "M5 6h14M5 12h14M5 18h14"
    },
    {
      id: "products",
      label: "Prodotti",
      color: "blue",
      icon: "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
    },
    {
      id: "recipes",
      label: "Ricette",
      color: "orange",
      icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
    },
    {
      id: "supermarkets",
      label: "Negozi",
      color: "purple",
      icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
    },
    {
      id: "profile",
      label: "Profilo",
      color: "gray",
      icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
    }
  ];

  const container = document.getElementById("quick-actions");

  container.innerHTML = actions.map(a => `
    <button class="action-btn" onclick="navigate('${a.id}')">
      <div class="action-icon ${a.color}">
        <svg class="icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${a.icon}" />
        </svg>
      </div>
      <span class="action-label">${a.label}</span>
    </button>
  `).join("");
}


function renderOffers(products, supermarkets) {
  // Prendi solo i prodotti con sconto reale
  const discounted = products
    .filter(p => p.discounted_price !== null && p.original_price !== null)
    .slice(0, 4);

  const container = document.getElementById("offers");

  if (!discounted.length) {
    container.innerHTML = `<p>Nessuna offerta disponibile al momento.</p>`;
    return;
  }

  container.innerHTML = discounted.map(p => {
    const sm = supermarkets.find(s => s.id === p.supermarket_id);

    const oldPrice = p.original_price;
    const newPrice = p.discounted_price;
    const discount = Math.round((1 - newPrice / oldPrice) * 100);

    return `
      <div class="offer-card" data-id="${p.id}">


        <div class="offer-img-wrapper">
          <img src="${p.image}" class="offer-img">
          <div class="discount-badge">-${discount}%</div>
        </div>

        <div class="offer-sm">
          <div class="offer-sm-icon">
            <img src="${sm.image}" alt="">
          </div>
          <span class="offer-sm-name">${sm.name}</span>
        </div>

        <div class="offer-name">${p.name}</div>

        <div class="offer-price">
          <span class="new-price">${newPrice.toFixed(2).replace(".", ",")} €</span>
          <span class="old-price">${oldPrice.toFixed(2).replace(".", ",")} €</span>
        </div>

      </div>
    `;
  }).join("");

  document.querySelectorAll(".offer-card").forEach(card => {
  card.addEventListener("click", () => {
    const id = Number(card.dataset.id);
    openProductModalFromDashboard(id);
  });
});

}



function renderRecipe(recipes) {
  if (!recipes.length) {
  console.log('Recipe not found') ;
  return;
  }

  const r = recipes[0];
  const section = document.getElementById("recipe-section");
  const card = document.getElementById("recipe-card");

  section.style.display = "block";

  card.innerHTML = `
    <img src="${r.image}">
    <div class="recipe-overlay">
      <h3>${r.name}</h3>
      <p>Un primo piatto fresco, veloce e nutriente, perfetto per un pranzo leggero ma gustoso. La unione della cremosità dell avocado con la sapidità del salmone crea un equilibrio perfetto.</p>
    </div>
  `;
}

function navigate(tab) {
  // reset
  document.querySelectorAll(".nav-pill").forEach(btn => btn.classList.remove("active"));

  // trova il pulsante giusto
  const active = [...document.querySelectorAll(".nav-pill")]
    .find(btn => btn.textContent.toLowerCase() === tab.toLowerCase());

  if (active) active.classList.add("active");

  // redirect
  if (tab === "home") window.location.href = "dashboard.html";
  if (tab === "products") window.location.href = "products.html";
  if (tab === "recipes") window.location.href = "recipes.html";
  if (tab === "supermarkets") window.location.href = "supermarkets.html";
  if (tab === "profile") window.location.href = "profile.html";
  if (tab === "list") window.location.href = "shopping-list.html";
}


loadDashboard();
function goToAllOffers() {
  window.location.href = "products.html?sale=1";
}

document.getElementById("see-all-offers")
  .addEventListener("click", goToAllOffers);

document.querySelectorAll(".nav-pill").forEach(btn => {
  btn.addEventListener("click", () => {
    const tab = btn.dataset.tab;
    navigate(tab);
  });
});


function openProductModalFromDashboard(productId) {
  const product = window.__allProducts.find(p => p.id === productId);
  const supermarket = window.__allSupermarkets.find(s => s.id === product.supermarket_id);

  if (!product || !supermarket) return;

  // usa la stessa funzione della pagina prodotti
  openProductModal(product, supermarket);
}
