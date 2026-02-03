const token = localStorage.getItem("token");
if (!token) window.location.href = "index.html";

let supermarkets = []
let products = []

async function loadSupermarkets() {
    const token = localStorage.getItem("token")

    const res = await apiFetch("http://localhost:8000/supermarket", {
        headers: {
            "Authorization": "Bearer " + token
        }
    })

    return res.ok ? res.json() : []
}

async function loadProducts() {
    const token = localStorage.getItem("token")

    const res = await apiFetch("http://localhost:8000/product", {
        headers: {
            "Authorization": "Bearer " + token
        }
    })

    return res.ok ? res.json() : []
}

async function init() {
    supermarkets = await loadSupermarkets()
    products = await loadProducts()
    showSupermarkets()
}

init()


const pageList = document.getElementById("supermarkets-page");
const pageDetails = document.getElementById("supermarket-details");
const listContainer = document.getElementById("supermarket-list");
const headerContainer = document.getElementById("sm-header");
const productsGrid = document.getElementById("products-grid");
const backBtn = document.getElementById("back-btn");
const BASE_URL = "http://localhost:8000"

function showSupermarkets() {
    pageDetails.classList.add("hidden");
    pageList.classList.remove("hidden");

    listContainer.innerHTML = "";

    supermarkets.forEach(sm => {
        const card = document.createElement("div");
        card.className = "supermarket-card";
        card.innerHTML = `
            <div class="supermarket-logo">
                <img src="${BASE_URL + sm.image}">
            </div>
            <div class="flex-1">
                <h3 class="text-lg font-bold text-gray-800">${sm.name}</h3>
                <p class="text-sm text-gray-500">${sm.location}</p>
            </div>
        `;
        card.addEventListener("click", () => showDetails(sm));
        listContainer.appendChild(card);
    });
}

function showDetails(sm) {
    pageList.classList.add("hidden");
    pageDetails.classList.remove("hidden");

    headerContainer.innerHTML = `
        <img src="${BASE_URL + sm.image}">
        <div>
            <h1 class="title">${sm.name}</h1>
            <p class="text-gray-500">${sm.location}</p>
        </div>
    `;

    const smProducts = products.filter(p => p.supermarket_id === sm.id);

productsGrid.innerHTML = smProducts.map(p => {
    const hasDiscount = p.discounted_price !== null;

    return `
        <div class="product-card" onclick='openProductModal(${JSON.stringify(p)}, ${JSON.stringify(sm)})'>
            ${hasDiscount ? `<div class="discount-badge">-${Math.round((1 - p.discounted_price / p.original_price) * 100)}%</div>` : ""}
            <img src="${BASE_URL + p.image}">
            <h4>${p.name}</h4>

            <p class="price">
                ${hasDiscount
                    ? `<span class="discounted">${p.original_price.toFixed(2).replace('.', ',')} €</span>
                       <span class="final-price">${p.discounted_price.toFixed(2).replace('.', ',')} €</span>`
                    : `<span class="final-price">${p.original_price.toFixed(2).replace('.', ',')} €</span>`
                }
            </p>
        </div>
    `;
}).join("");


}

backBtn.addEventListener("click", showSupermarkets);

