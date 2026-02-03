// Attiva automaticamente il tab corretto
window.addEventListener("DOMContentLoaded", () => {
  const current = document.body.dataset.page;
  const links = document.querySelectorAll(".nav-pill");

  links.forEach(btn => {
    if (btn.dataset.tab === current) {
      btn.classList.add("active");
    }
  });
});

// Navigazione tra pagine
function navigate(tab) {
  if (tab === "home") window.location.href = "dashboard.html";
  if (tab === "list") window.location.href = "shopping-list.html";
  if (tab === "products") window.location.href = "products.html";
  if (tab === "recipes") window.location.href = "recipes.html";
  if (tab === "supermarkets") window.location.href = "supermarkets.html";
  if (tab === "profile") window.location.href = "profile.html";
}
