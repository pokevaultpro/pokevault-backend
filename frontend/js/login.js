import CONFIG from "./config.js";

const form = document.getElementById("login-form");
const errorBox = document.getElementById("error-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBox.classList.add("hidden");

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/auth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        username: username,   // <-- FastAPI si aspetta "username"
        password: password // <-- e "password"
      })
    });

    if (!res.ok) {
      errorBox.textContent = "Invalid email or password";
      errorBox.classList.remove("hidden");
      return;
    }

    const data = await res.json();

    // salva il token JWT
    localStorage.setItem("token", data.access_token);

    // redirect alla dashboard
    window.location.href = "dashboard.html";

  } catch (err) {
    errorBox.textContent = "Network error. Try again later.";
    errorBox.classList.remove("hidden");
  }
});
document.getElementById("register-btn").addEventListener("click", () => {
  window.location.href = "register.html";
});
