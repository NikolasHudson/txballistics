/* ===========================================================
   TX Ballistics — Homepage interactivity
   - Render featured product cards
   - Add-to-cart counter
   - Rotating testimonials
   =========================================================== */

/* ---------- Featured products data ---------- */
const PRODUCTS = [
  {
    caliber: "5.56", title: "5.56 NATO — 55gr FMJ — Federal — 1000 Rounds",
    rating: 5, reviews: 412, price: 469.99, was: 529.99, cpr: "47¢",
    stock: 38, tested: true,
    specs: ["1,000 rounds", "Federal", "FMJ", "Brass case"]
  },
  {
    caliber: ".45", title: ".45 ACP — 230gr FMJ — Magtech — 500 Rounds",
    rating: 5, reviews: 188, price: 274.99, was: null, cpr: "55¢",
    stock: 9, tested: false,
    specs: ["500 rounds", "Magtech", "FMJ", "Brass case"]
  },
  {
    caliber: ".308", title: ".308 Win — 150gr SP — Hornady — 200 Rounds",
    rating: 4, reviews: 96, price: 229.99, was: 259.99, cpr: "115¢",
    stock: 21, tested: true,
    specs: ["200 rounds", "Hornady", "Soft Point", "Brass case"]
  },
  {
    caliber: "12GA", title: "12 Gauge — 00 Buck — Winchester — 250 Rounds",
    rating: 5, reviews: 143, price: 199.99, was: 224.99, cpr: "80¢",
    stock: 4, tested: false,
    specs: ["250 rounds", "Winchester", "00 Buckshot", "2¾ in"]
  },
  {
    caliber: ".22LR", title: ".22 LR — 40gr LRN — CCI — 2000 Rounds",
    rating: 5, reviews: 521, price: 159.99, was: null, cpr: "8¢",
    stock: 60, tested: true,
    specs: ["2,000 rounds", "CCI", "Lead Round Nose", "Rimfire"]
  }
];

function star(n) { return "★★★★★".slice(0, n) + "☆☆☆☆☆".slice(0, 5 - n); }

function renderProducts() {
  const wrap = document.getElementById("product-list");
  if (!wrap) return;
  wrap.innerHTML = PRODUCTS.map(p => {
    const lowStock = p.stock <= 10;
    const priceBlock = p.was
      ? `<span class="pc-was">$${p.was.toFixed(2)}</span><span class="pc-price sale">$${p.price.toFixed(2)}</span>`
      : `<span class="pc-price">$${p.price.toFixed(2)}</span>`;
    return `
      <article class="product-card">
        <span class="stock-badge ${lowStock ? "low" : ""}">${p.stock} IN STOCK</span>
        <div class="pc-img">${p.caliber}</div>
        <div class="pc-body">
          ${p.tested ? '<span class="tested-badge">TESTED</span>' : ""}
          <h3>${p.title}</h3>
          <div class="pc-rating">${star(p.rating)} <span>(${p.reviews} reviews)</span></div>
          <ul class="pc-specs">${p.specs.map(s => `<li>${s}</li>`).join("")}</ul>
        </div>
        <div class="pc-buy">
          <div>${priceBlock}</div>
          <span class="pc-cpr">${p.cpr} / round</span>
          <button class="btn btn-primary btn-block add-to-cart">Add to Cart</button>
        </div>
      </article>`;
  }).join("");
}

/* ---------- Cart counter ---------- */
function wireCart() {
  const countEl = document.querySelector(".cart-count");
  let count = 0;
  document.body.addEventListener("click", e => {
    const btn = e.target.closest(".add-to-cart");
    if (!btn) return;
    count += 1;
    if (countEl) countEl.textContent = count;
    const original = btn.textContent;
    btn.textContent = "✓ Added!";
    btn.disabled = true;
    setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 1200);
  });
}

/* ---------- Rotating testimonials ---------- */
const QUOTES = [
  { text: "Reserved Thursday, picked it up Saturday morning. Counts were exactly right and they had it bagged and ready. This is my shop now.", who: "Dale R., Round Rock" },
  { text: "Finally a dealer that actually has what the site says they have. No backorder games.", who: "Marisol T., San Antonio" },
  { text: "Grabbed a case of 5.56 for a training class. Best price I found and it was waiting at the counter.", who: "Coach Vance, Killeen" },
  { text: "Called with a dumb question about grain weight and they spent ten minutes helping. Real people.", who: "Jenny K., Waco" }
];

function wireTestimonials() {
  const wrap = document.getElementById("testimonials");
  if (!wrap) return;
  let i = 0;
  function render() {
    const q = QUOTES[i];
    wrap.innerHTML = `
      <div class="quote-stars">★★★★★</div>
      <p class="quote">"${q.text}"<span class="quote-author">— ${q.who}</span></p>
      <div class="quote-dots">
        ${QUOTES.map((_, idx) => `<button class="${idx === i ? "active" : ""}" data-i="${idx}" aria-label="Quote ${idx + 1}"></button>`).join("")}
      </div>`;
  }
  wrap.addEventListener("click", e => {
    const dot = e.target.closest("[data-i]");
    if (!dot) return;
    i = Number(dot.dataset.i);
    render();
  });
  render();
  setInterval(() => { i = (i + 1) % QUOTES.length; render(); }, 5000);
}

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", () => {
  renderProducts();
  wireCart();
  wireTestimonials();
});
