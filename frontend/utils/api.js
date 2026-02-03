async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    "Authorization": `Bearer ${token}`
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    logoutUser();
    return;
  }

  return response;
}

function logoutUser() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}
