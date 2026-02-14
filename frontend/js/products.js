    import CONFIG from "./config.js";
    import { openProductModal } from "./modal-function.js";

    document.addEventListener("DOMContentLoaded", () => {
        loadProducts();
        updateVisibleRange();
    });

    let allProducts = [];
    let supermarkets = [];
    let currentCategory = "all";
    let currentStore = "all";
    let favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
    let visibleStart = 0;
    let visibleEnd = 0;

    let CARD_HEIGHT = 260; // desktop
    let CARD_HEIGHT_MOBILE = 300; // mobile
    let BUFFER = 10; // quante card extra mostrare
    let filtered = [];



    function toggleFavorite(id) {
      if (favorites.includes(id)) {
        favorites = favorites.filter(f => f !== id);
      } else {
        favorites.push(id);
      }
      localStorage.setItem("favorites", JSON.stringify(favorites));
      renderProducts();
    }

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
      const search = document.getElementById("search-input").value.toLowerCase();

      // 1. FILTRO
      filtered = allProducts.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(search);
        const matchesCategory =
          currentCategory === "all" ||
          (currentCategory === "sale" && p.discounted_price !== null) ||
          (currentCategory === "favorites" && favorites.includes(p.id)) ||
          p.category === currentCategory;

        const matchesStore =
          currentStore === "all" ||
          p.supermarket_id == currentStore;

        return matchesSearch && matchesCategory && matchesStore;
      });

      // 2. ORDINAMENTO
      if (currentStore === "all") {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
      } else {
        filtered.sort((a, b) => {
          const aOrder = a.aisle_order ?? 9999;
          const bOrder = b.aisle_order ?? 9999;
          return aOrder - bOrder;
        });
      }

      // 3. CALCOLO ALTEZZA CARD (mobile vs desktop)
      const isMobile = window.innerWidth < 480;
      const cardHeight = isMobile ? CARD_HEIGHT_MOBILE : CARD_HEIGHT;

      // 4. ALTEZZA TOTALE DELLA LISTA
      const totalHeight = filtered.length * cardHeight;

      const container = document.getElementById("virtual-container");
container.style.height = totalHeight + "px";

      document.getElementById("spacer-top").style.height = "0px";
      updateVisibleRange();
    }

    function updateVisibleRange() {
  const container = document.getElementById("virtual-container");
  if (!container) return;

  const viewportHeight = window.innerHeight;

  const isMobile = window.innerWidth < 480;
  const cardHeight = isMobile ? CARD_HEIGHT_MOBILE : CARD_HEIGHT;

  const containerTop = container.getBoundingClientRect().top;
  const scrollTop = Math.max(0, -containerTop);

  const startIndex = Math.floor(scrollTop / cardHeight) - BUFFER;
  const endIndex = Math.ceil((scrollTop + viewportHeight) / cardHeight) + BUFFER;

  visibleStart = Math.max(0, startIndex);
  visibleEnd = Math.min(filtered.length, endIndex);

  renderVirtualProducts();
}

    function renderVirtualProducts() {
      const grid = document.getElementById("products-grid");

      // 🔥 Cancella solo le card, NON gli spacer
      [...grid.querySelectorAll(".product-card")].forEach(el => el.remove());

      const isMobile = window.innerWidth < 480;
      const cardHeight = isMobile ? CARD_HEIGHT_MOBILE : CARD_HEIGHT;

      const spacing = isMobile ? 20 : 0;
        grid.style.height = (filtered.length * (cardHeight + spacing)) + "px";


      const slice = filtered.slice(visibleStart, visibleEnd);

      slice.forEach((p, i) => {
        const realIndex = visibleStart + i;
        const card = createProductCard(p);

        card.style.position = "absolute";

        const spacing = isMobile ? 20 : 0; // spazio tra card su mobile
        card.style.top = (realIndex * (cardHeight + spacing)) + "px";

        card.style.left = "0";
        card.style.right = "0";

        grid.appendChild(card);
      });

      document.getElementById("spacer-top").style.height =
        (visibleStart * cardHeight) + "px";

      document.getElementById("spacer-bottom").style.height =
        ((filtered.length - visibleEnd) * cardHeight) + "px";
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

    function createProductCard(p) {
      const hasDiscount = p.discounted_price !== null;
      const supermarket = supermarkets.find(s => s.id === p.supermarket_id);
      const supermarketName = supermarket ? supermarket.name : "";

      const card = document.createElement("div");
      card.className = "product-card";

    card.innerHTML = `
        <div class="img-wrapper">

          ${hasDiscount ? `
            <div class="discount-badge">
              -${Math.round((1 - p.discounted_price / p.original_price) * 100)}%
            </div>` : ""
          }

          <img loading="lazy"
               src="${p.image}"
               class="product-img"
               onerror="this.src='/static/images/placeholder.jpg'">

          <div class="fav-icon ${favorites.includes(p.id) ? "active" : ""}" data-id="${p.id}">
            <svg viewBox="0 0 24 24" class="heart-svg">
              <path d="M12 21s-6-4.35-9-8.7C-1.5 7.5 1.5 3 6 3c2.25 0 4.5 1.5 6 3.75C13.5 4.5 15.75 3 18 3c4.5 0 7.5 4.5 3 9.3C18 16.65 12 21 12 21z"/>
            </svg>
          </div>

        </div>

        <div class="product-info">

          <div class="product-name">${p.name}</div>

          <div class="product-meta-row">
            <span class="product-brand">${supermarketName}</span>
            <span class="product-category">${p.category}</span>
          </div>

          <div class="nutri-row">
            ${p.calories ? `<span class="nutri-badge">CAL ${p.calories}</span>` : ""}
            ${p.protein ? `<span class="nutri-badge">PROT ${p.protein}g</span>` : ""}
          </div>

          <div class="price-row">
            ${
              hasDiscount
                ? `
                  <span class="old-price">€ ${p.original_price.toFixed(2).replace(".", ",")}</span>
                  <span class="new-price">€ ${p.discounted_price.toFixed(2).replace(".", ",")}</span>
                `
                : `
                  <span class="regular-price">€ ${p.original_price.toFixed(2).replace(".", ",")}</span>
                `
            }
            <span class="unit-tag">/ ${p.unit || "pz"}</span>
          </div>

          <button class="add-btn" data-id="${p.id}">
            + Aggiungi
          </button>

        </div>
      `;

      // ❤️ CLICK SUL CUORE
      const favBtn = card.querySelector(".fav-icon");
      favBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleFavorite(p.id);
      });

      // 🛒 CLICK SU AGGIUNGI
      card.querySelector(".add-btn").addEventListener("click", (event) => {
        event.stopPropagation();
        addToCart(p.id);
      });

      // 📄 MODAL
      card.addEventListener("click", () => {
        openProductModal(p, supermarket);
      });

      return card;
    }

    function syncStickyOffset() {
      const sticky = document.querySelector(".sticky-header");
      const page = document.querySelector(".products-page");

      if (!sticky || !page) return;

      const navbarHeight = document.querySelector(".top-header")?.offsetHeight || 60;
      page.style.paddingTop = sticky.offsetHeight + navbarHeight + "px";
    }

    window.addEventListener("load", syncStickyOffset);
    window.addEventListener("resize", syncStickyOffset);



    window.addEventListener("scroll", updateVisibleRange);
    window.addEventListener("resize", renderProducts);
