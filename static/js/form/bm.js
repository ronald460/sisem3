const inputCedula = document.getElementById("bm");
let oldValue = "";

inputCedula.addEventListener("input", function (e) {
  let cursorPos = this.selectionStart;
  let value = this.value;

  // Si el campo está vacío, no hacemos nada
  if (value === "") {
    oldValue = "";
    return;
  }

  // Eliminar cualquier cosa que no sea número
  let numbers = value.replace(/[^0-9]/g, "");

  // Si no hay números, vaciar el campo
  if (numbers === "") {
    this.value = "";
    oldValue = "";
    return;
  }

  // Construir el nuevo valor con V-
  let newValue = "C.I N°-" + numbers;

  // Actualizar el valor si es diferente
  if (newValue !== this.value) {
    this.value = newValue;

    // Ajustar la posición del cursor
    let newCursorPos = cursorPos + (newValue.length - value.length);
    this.setSelectionRange(newCursorPos, newCursorPos);
  }

  oldValue = newValue;
});

// Evitar que el usuario borre el prefijo
inputCedula.addEventListener("keydown", function (e) {
  if (this.selectionStart <= 2 && e.key === "Backspace") {
    e.preventDefault();
  }
});

// Al enfocar, si está vacío, poner el prefijo
inputCedula.addEventListener("focus", function () {
  if (this.value === "") {
    this.value = "C.I N°-";
    this.setSelectionRange(2, 2);
  }
});

// Al salir, si solo tiene el prefijo, vaciar
inputCedula.addEventListener("blur", function () {
  if (this.value === "V-") {
    this.value = "";
  }
});
