/* ===========================================================
   TX Ballistics — Cart page interactivity
   - Quantity steppers update line + order totals
   - Remove line items, show empty state
   =========================================================== */

const TAX_RATE = 0.0825;

function money(n) { return "$" + n.toFixed(2); }

function recalc() {
  const items = [...document.querySelectorAll(".cart-item")].filter(el => !el.dataset.removed);
  let subtotal = 0;
  let unitCount = 0;

  items.forEach(item => {
    const price = parseFloat(item.dataset.price);
    const qty = parseInt(item.dataset.qty, 10) || 1;
    const line = price * qty;
    subtotal += line;
    unitCount += qty;
    item.querySelector(".ci-line-price").textContent = money(line);
  });

  const tax = subtotal * TAX_RATE;
  const total = subtotal + tax;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set("os-subtotal", money(subtotal));
  set("os-tax", money(tax));
  set("os-total", money(total));
  set("cart-item-count", items.length);

  // Header cart badge counts distinct line items
  const badge = document.querySelector(".cart-count");
  if (badge) badge.textContent = items.length;

  // Empty state toggle
  const empty = document.getElementById("cart-empty");
  const summary = document.getElementById("order-summary");
  const list = document.getElementById("cart-items");
  if (items.length === 0) {
    if (empty) empty.hidden = false;
    if (summary) summary.style.display = "none";
    if (list) list.style.display = "none";
  }
}

function wireCart() {
  document.addEventListener("click", e => {
    const item = e.target.closest(".cart-item");

    // Quantity steppers
    if (e.target.closest(".qty-plus") && item) {
      let q = parseInt(item.dataset.qty, 10) || 1;
      q = Math.min(q + 1, 99);
      item.dataset.qty = q;
      item.querySelector(".qty-input").value = q;
      recalc();
      return;
    }
    if (e.target.closest(".qty-minus") && item) {
      let q = parseInt(item.dataset.qty, 10) || 1;
      q = Math.max(q - 1, 1);
      item.dataset.qty = q;
      item.querySelector(".qty-input").value = q;
      recalc();
      return;
    }

    // Remove
    if (e.target.closest(".ci-remove") && item) {
      item.classList.add("removing");
      item.dataset.removed = "true";
      setTimeout(() => { item.remove(); recalc(); }, 250);
      recalc();
      return;
    }
  });

  // Manual typing in qty field
  document.addEventListener("input", e => {
    if (!e.target.classList.contains("qty-input")) return;
    const item = e.target.closest(".cart-item");
    let q = parseInt(e.target.value.replace(/\D/g, ""), 10);
    if (!q || q < 1) q = 1;
    item.dataset.qty = q;
    recalc();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireCart();
  recalc();
});
