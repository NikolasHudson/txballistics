/* ===========================================================
   TX Ballistics — Product Detail page interactivity
   - Quantity stepper (updates running total)
   - Gallery thumbnail switching
   - Add-to-cart counter
   =========================================================== */

const UNIT_PRICE = 249.99;
const ROUNDS_PER_UNIT = 1000;

/* ---------- Quantity stepper + live total ---------- */
function wireQty() {
  const input = document.getElementById("qty");
  const minus = document.getElementById("qty-minus");
  const plus  = document.getElementById("qty-plus");
  const totalEl = document.getElementById("buy-total");
  const roundsEl = document.getElementById("buy-rounds");
  if (!input) return;

  function clamp(n) { return Math.max(1, Math.min(20, n)); }
  function update() {
    const q = clamp(parseInt(input.value, 10) || 1);
    input.value = q;
    if (totalEl) totalEl.textContent = "$" + (q * UNIT_PRICE).toFixed(2);
    if (roundsEl) roundsEl.textContent = (q * ROUNDS_PER_UNIT).toLocaleString() + " rounds";
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
  wireCart();
});
