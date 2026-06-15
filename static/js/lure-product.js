/* ===========================================================
   TX Ballistics — Fishing Lure product page interactivity
   - Quantity stepper (updates running total)
   - Gallery thumbnail switching
   - Color/pattern swatch picker
   - Add-to-cart counter
   =========================================================== */

const UNIT_PRICE = 8.99;

/* ---------- Quantity stepper + live total ---------- */
function wireQty() {
  const input = document.getElementById("qty");
  const minus = document.getElementById("qty-minus");
  const plus  = document.getElementById("qty-plus");
  const totalEl = document.getElementById("buy-total");
  const qtyEl = document.getElementById("buy-qty");
  if (!input) return;

  function clamp(n) { return Math.max(1, Math.min(99, n)); }
  function update() {
    const q = clamp(parseInt(input.value, 10) || 1);
    input.value = q;
    if (totalEl) totalEl.textContent = "$" + (q * UNIT_PRICE).toFixed(2);
    if (qtyEl) qtyEl.textContent = q + (q === 1 ? " lure" : " lures");
  }
  minus && minus.addEventListener("click", () => { input.value = clamp((parseInt(input.value, 10) || 1) - 1); update(); });
  plus  && plus.addEventListener("click",  () => { input.value = clamp((parseInt(input.value, 10) || 1) + 1); update(); });
  input.addEventListener("input", update);
  update();
}

/* ---------- Gallery thumbnails ---------- */
function wireGallery() {
  const main = document.getElementById("gallery-main-label");
  const thumbs = document.querySelectorAll(".gallery-thumbs button");
  thumbs.forEach(btn => {
    btn.addEventListener("click", () => {
      thumbs.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      if (main) main.textContent = btn.dataset.label || btn.textContent;
    });
  });
}

/* ---------- Color / pattern swatch picker ---------- */
function wireSwatches() {
  const nameEl = document.getElementById("swatch-name");
  const swatches = document.querySelectorAll("#swatches .swatch");
  swatches.forEach(sw => {
    sw.addEventListener("click", () => {
      swatches.forEach(s => s.classList.remove("active"));
      sw.classList.add("active");
      if (nameEl && sw.dataset.name) nameEl.textContent = sw.dataset.name;
    });
  });
}

/* ---------- Cart counter ---------- */
function wireCart() {
  const countEl = document.querySelector(".cart-count");
  let count = 0;
  document.body.addEventListener("click", e => {
    const btn = e.target.closest(".add-to-cart");
    if (!btn || btn.disabled) return;
    const qtyInput = document.getElementById("qty");
    const add = btn.id === "main-add" && qtyInput ? (parseInt(qtyInput.value, 10) || 1) : 1;
    count += add;
    if (countEl) countEl.textContent = count;
    const original = btn.textContent;
    btn.textContent = "✓ Added to Cart";
    setTimeout(() => { btn.textContent = original; }, 1200);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireQty();
  wireGallery();
  wireSwatches();
  wireCart();
});
