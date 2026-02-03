import CONFIG from "./config.js";
import { openProductModal } from "./modal-function.js";


const token = localStorage.getItem("token");
if (!token) window.location.href = "index.html";

let supermarkets = []
let products = []

async function loadSupermarkets() {
    const token = localStorage.getItem("token")

    const res = await apiFetch(`${CONFIG.API_BASE_URL}/supermarket`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })

    return res.ok ? res.json() : []
}

async function loadProducts() {
    const token = localStorage.getItem("token")

    const res = await apiFetch(`${CONFIG.API_BASE_URL}/product`, {
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


function showSupermarkets() {
    pageDetails.classList.add("hidden");
    pageList.classList.remove("hidden");

    listContainer.innerHTML = "";

    supermarkets.forEach(sm => {
        const card = document.createElement("div");
        card.className = "supermarket-card";
        card.innerHTML = `
            <div class="supermarket-logo">
                <img src="${sm.image}">
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
        <img src="${sm.image}">
        <div>
            <h1 class="title">${sm.name}</h1>
            <p class="text-gray-500">${sm.location}</p>
        </div>
    `;

    const smProducts = products.filter(p => p.supermarket_id === sm.id);

    productsGrid.innerHTML = smProducts.map(p => {
        const hasDiscount = p.discounted_price !== null;

        return `
            <div class="product-card" data-id="${p.id}">
                ${hasDiscount ? `<div class="discount-badge">-${Math.round((1 - p.discounted_price / p.original_price) * 100)}%</div>` : ""}
                <img src="${p.image}">
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

    // ⭐ AGGIUNGI I LISTENER QUI
    document.querySelectorAll(".product-card").forEach(card => {
        card.addEventListener("click", () => {
            const id = Number(card.dataset.id);
            const product = products.find(p => p.id === id);
            openProductModal(product, sm);
        });
    });
}


backBtn.addEventListener("click", showSupermarkets);

