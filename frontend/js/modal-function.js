export function openProductModal(item, supermarket) {

  // ===== IMMAGINE E INFO BASE =====
  document.getElementById("modal-image").src = item.image;
  document.getElementById("modal-category").textContent = item.category || "Prodotto";
  document.getElementById("modal-name").textContent = item.name;

  // ===== SUPERMERCATO =====
  document.getElementById("modal-store").textContent = supermarket.name;
  document.getElementById("modal-location").textContent = item.location;

  // ===== PREZZO + SCONTO =====
  if (item.discounted_price) {
    const discountPerc = Math.round((1 - item.discounted_price / item.original_price) * 100);

    document.getElementById("modal-price").innerHTML = `
      <span class="discounted">${item.original_price.toFixed(2).replace('.', ',')} €</span>
      <span class="final-price">${item.discounted_price.toFixed(2).replace('.', ',')} €</span>
    `;

    const badge = document.getElementById("modal-discount-badge");
    badge.textContent = `-${discountPerc}%`;
    badge.classList.remove("hidden");

  } else {
    document.getElementById("modal-price").innerHTML =
      `<span class="final-price">${item.original_price.toFixed(2).replace('.', ',')} €</span>`;

    document.getElementById("modal-discount-badge").classList.add("hidden");
  }

  // ===== NUTRIZIONALI =====
  const grid = document.getElementById("modal-nutrition-grid");
  grid.innerHTML = "";

  const cards = [
    { label: "Calorie", value: item.calories, unit: "kcal" },
    { label: "Grassi", value: item.fat, unit: "g" },
    { label: "Carboidrati", value: item.carbs, unit: "g" },
    { label: "Proteine", value: item.protein, unit: "g" }
  ];

  cards.forEach(c => {
    const div = document.createElement("div");
    div.className = "nutri-card";
    div.innerHTML = `
      <div class="nutri-label">${c.label}</div>
      <div class="nutri-value">${c.value ?? "-"} ${c.unit}</div>
    `;
    grid.appendChild(div);
  });

  // ===== MOSTRA MODAL =====
  document.getElementById("product-modal").classList.remove("hidden");
}

export function closeModal() {
  document.getElementById("product-modal").classList.add("hidden");
}

