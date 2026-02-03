const form = document.getElementById("register-form");
const errorBox = document.getElementById("error-box");
const successBox = document.getElementById("success-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBox.classList.add("hidden");
  successBox.classList.add("hidden");

  const payload = {
    username: document.getElementById("username").value.trim(),
    email: document.getElementById("email").value.trim(),
    first_name: document.getElementById("first_name").value.trim(),
    last_name: document.getElementById("last_name").value.trim(),
    password: document.getElementById("password").value.trim(),
    role: "user"
  };

  try {
    const res = await fetch("http://localhost:8000/auth", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const data = await res.json();
      errorBox.textContent = data.detail || "Registration failed";
      errorBox.classList.remove("hidden");
      return;
    }

    successBox.textContent = "Account created successfully! Redirecting...";
    successBox.classList.remove("hidden");

    setTimeout(() => {
      window.location.href = "index.html";
    }, 1500);

  } catch (err) {
    errorBox.textContent = "Network error. Try again later.";
    errorBox.classList.remove("hidden");
  }
});
document.getElementById("login-btn").addEventListener("click", () => {
  window.location.href = "index.html";
});

