const inputTelefono = document.getElementById("telefono");

inputTelefono.addEventListener("input", function (e) {
  let value = this.value.replace(/\D/g, ""); // Eliminar todo lo que no sea número

  if (value.length > 0) {
    // Formato: 0424-1234567
    if (value.length <= 4) {
      this.value = value;
    } else if (value.length <= 11) {
      this.value = value.slice(0, 4) + "-" + value.slice(4, 11);
    } else {
      this.value = value.slice(0, 4) + "-" + value.slice(4, 11);
    }
  } else {
    this.value = "";
  }
});

// Opcional: Validar que solo sean números mientras se escribe
inputTelefono.addEventListener("keydown", function (e) {
  // Permitir teclas de control (backspace, delete, tab, etc.)
  const teclasPermitidas = [
    "Backspace",
    "Delete",
    "Tab",
    "ArrowLeft",
    "ArrowRight",
    "ArrowUp",
    "ArrowDown",
    "Home",
    "End",
  ];

  if (teclasPermitidas.includes(e.key)) {
    return;
  }

  // Prevenir letras y caracteres especiales
  if (!/^[0-9]$/.test(e.key) && e.key !== "-") {
    e.preventDefault();
  }
});
