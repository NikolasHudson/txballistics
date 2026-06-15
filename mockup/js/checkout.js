/* ===========================================================
   TX Ballistics — Checkout page interactivity
   - Highlight selected store / payment options
   - Toggle card fields based on payment choice
   - Mock "Place Order" confirmation
   =========================================================== */

function syncSelected(name) {
  const options = document.querySelectorAll(`input[name="${name}"]`);
  options.forEach(input => {
    const wrap = input.closest(".store-option, .pay-option");
    if (wrap) wrap.classList.toggle("selected", input.checked);
  });
}

function toggleCardFields() {
  const cardFields = document.querySelector(".card-fields");
  if (!cardFields) return;
  const payNow = document.querySelector('input[name="pay"]');
  cardFields.style.display = payNow && payNow.checked ? "" : "none";
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[name="store"]').forEach(i =>
    i.addEventListener("change", () => syncSelected("store")));

  document.querySelectorAll('input[name="pay"]').forEach(i =>
    i.addEventListener("change", () => { syncSelected("pay"); toggleCardFields(); }));

  const place = document.querySelector(".cs-place");
  if (place) {
    place.addEventListener("click", () => {
      place.textContent = "✓ Order Placed!";
      place.disabled = true;
      setTimeout(() => { window.location.href = "confirmation.html"; }, 600);
    });
  }
});
