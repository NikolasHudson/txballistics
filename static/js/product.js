/* TX Ballistics — product detail: qty stepper (live total) + variant swatches */
(function () {
  const input = document.getElementById("qty");
  const minus = document.getElementById("qty-minus");
  const plus = document.getElementById("qty-plus");
  const totalEl = document.getElementById("buy-total");
  const addBtn = document.getElementById("main-add");

  function unitPrice() {
    return parseFloat(addBtn ? addBtn.dataset.unitPrice : "0") || 0;
  }
  function clamp(n) { return Math.max(1, Math.min(99, n)); }
  function update() {
    if (!input) return;
    const q = clamp(parseInt(input.value, 10) || 1);
    input.value = q;
    if (totalEl) totalEl.textContent = "$" + (q * unitPrice()).toFixed(2);
  }
  if (minus) minus.addEventListener("click", () => { input.value = clamp((parseInt(input.value, 10) || 1) - 1); update(); });
  if (plus) plus.addEventListener("click", () => { input.value = clamp((parseInt(input.value, 10) || 1) + 1); update(); });
  if (input) input.addEventListener("input", update);

  // Variant swatch picker
  const swatches = document.querySelectorAll(".swatch");
  const nameEl = document.getElementById("swatch-name");
  const variantInput = document.getElementById("variant-id");
  swatches.forEach((btn) => {
    btn.addEventListener("click", () => {
      swatches.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      if (nameEl) nameEl.textContent = btn.dataset.name;
      if (variantInput) variantInput.value = btn.dataset.variant || "";
      if (addBtn && btn.dataset.price) addBtn.dataset.unitPrice = btn.dataset.price;
      update();
    });
  });

  update();
})();
