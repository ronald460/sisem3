// Detectar cuando el usuario intenta ir atrás
window.addEventListener("pageshow", function (event) {
  // Si la página viene del caché (botón atrás)
  if (
    event.persisted ||
    performance.getEntriesByType("navigation")[0].type === "back_forward"
  ) {
    window.location.href = "{% url 'home' %}";
  }
});
