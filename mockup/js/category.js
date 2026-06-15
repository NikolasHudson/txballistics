/* ===========================================================
   TX Ballistics — Category page (9mm Luger)
   Shared product data + two renderers:
     #cat-cards  -> horizontal card view (matches homepage)
     #cat-table  -> spreadsheet / table view with quantity on right
   =========================================================== */

const NINE_MM = [
  { cal: "9mm", title: "9mm Luger — 115gr FMJ — Blazer Brass", brand: "Blazer", bullet: "FMJ", grain: 115, casing: "Brass", rounds: 1000, rating: 5, reviews: 512, price: 249.99, was: 289.99, cprNum: 0.25, stock: 84, tested: true },
  { cal: "9mm", title: "9mm Luger — 124gr FMJ — Magtech", brand: "Magtech", bullet: "FMJ", grain: 124, casing: "Brass", rounds: 1000, rating: 5, reviews: 301, price: 259.99, was: null, cprNum: 0.26, stock: 47, tested: false },
  { cal: "9mm", title: "9mm Luger — 115gr FMJ — Winchester White Box", brand: "Winchester", bullet: "FMJ", grain: 115, casing: "Brass", rounds: 500, rating: 4, reviews: 188, price: 139.99, was: 154.99, cprNum: 0.28, stock: 23, tested: false },
  { cal: "9mm", title: "9mm Luger — 124gr JHP — Speer Gold Dot (Defense)", brand: "Speer", bullet: "JHP", grain: 124, casing: "Brass", rounds: 50, rating: 5, reviews: 96, price: 39.99, was: null, cprNum: 0.80, stock: 9, tested: true },
  { cal: "9mm", title: "9mm Luger — 147gr FMJ Subsonic — Federal", brand: "Federal", bullet: "FMJ", grain: 147, casing: "Brass", rounds: 500, rating: 5, reviews: 142, price: 164.99, was: 179.99, cprNum: 0.33, stock: 31, tested: true },
  { cal: "9mm", title: "9mm Luger — 115gr FMJ Steel Case — Tula", brand: "Tula", bullet: "FMJ", grain: 115, casing: "Steel", rounds: 1000, rating: 3, reviews: 64, price: 219.99, was: null, cprNum: 0.22, stock: 5, tested: false },
  { cal: "9mm", title: "9mm Luger — 124gr +P JHP — Hornady Critical Duty", brand: "Hornady", bullet: "JHP", grain: 124, casing: "Brass", rounds: 25, rating: 5, reviews: 77, price: 27.99, was: null, cprNum: 1.12, stock: 14, tested: true },
  { cal: "9mm", title: "9mm Luger — 115gr FMJ — PMC Bronze", brand: "PMC", bullet: "FMJ", grain: 115, casing: "Brass", rounds: 1000, rating: 4, reviews: 233, price: 244.99, was: 264.99, cprNum: 0.24, stock: 58, tested: false },
  { cal: "9mm", title: "9mm Luger — 124gr FMJ — Sellier & Bellot", brand: "S&B", bullet: "FMJ", grain: 124, casing: "Brass", rounds: 1000, rating: 4, reviews: 119, price: 234.99, was: null, cprNum: 0.23, stock: 0, tested: false },
  { cal: "9mm", title: "9mm Luger — 115gr JHP — Remington UMC", brand: "Remington", bullet: "JHP", grain: 115, casing: "Brass", rounds: 500, rating: 4, reviews: 88, price: 199.99, was: 219.99, cprNum: 0.40, stock: 12, tested: false }
];

const money = n => "$" + n.toFixed(2);
const cents = n => Math.round(n * 100) + "¢";
const star  = n => "★★★★★".slice(0, n) + "☆☆☆☆☆".slice(0, 5 - n);

function stockClass(s) { return s === 0 ? "out" : s <= 12 ? "low" : ""; }
function stockLabel(s) { return s === 0 ? "Out of Stock" : s + " in stock"; }

/* ---------- Variation A: cards (matches homepage product cards) ---------- */
function renderCards() {
  const wrap = document.getElementById("cat-cards");
  if (!wrap) return;
  wrap.innerHTML = NINE_MM.map(p => {
    const out = p.stock === 0;
    const priceBlock = p.was
      ? `<span class="pc-was">${money(p.was)}</span><span class="pc-price sale">${money(p.price)}</span>`
      : `<span class="pc-price">${money(p.price)}</span>`;
    return `
      <article class="product-card">
        <span class="stock-badge ${stockClass(p.stock)}">${out ? "OUT OF STOCK" : p.stock + " IN STOCK"}</span>
        <div class="pc-img">${p.cal}</div>
        <div class="pc-body">
          ${p.tested ? '<span class="tested-badge">TESTED</span>' : ""}
          <h3>${p.title}</h3>
          <div class="pc-rating">${star(p.rating)} <span>(${p.reviews} reviews)</span></div>
          <ul class="pc-specs">
            <li>${p.rounds.toLocaleString()} rounds</li>
            <li>${p.brand}</li>
            <li>${p.grain}gr ${p.bullet}</li>
            <li>${p.casing} case</li>
          </ul>
        </div>
        <div class="pc-buy">
          <div>${priceBlock}</div>
          <span class="pc-cpr">${cents(p.cprNum)} / round</span>
          <button class="btn btn-primary btn-block add-to-cart" ${out ? "disabled" : ""}>${out ? "Notify Me" : "Add to Cart"}</button>
        </div>
      </article>`;
  }).join("");
}

/* ---------- Variation B: spreadsheet / table view ---------- */
function renderTable() {
  const body = document.getElementById("cat-table");
  if (!body) return;
  body.innerHTML = NINE_MM.map(p => {
    const out = p.stock === 0;
    const priceBlock = p.was
      ? `<span class="t-was">${money(p.was)}</span><span class="t-price sale">${money(p.price)}</span>`
      : `<span class="t-price">${money(p.price)}</span>`;
    return `
      <tr>
        <td>
          <div class="tcell-product">
            <span class="tcell-thumb">${p.cal}</span>
            <span class="tcell-title">${p.title}
              ${p.tested ? '<span class="tested-inline"> ✓ TESTED</span>' : ""}
            </span>
          </div>
        </td>
        <td>${p.brand}</td>
        <td>${p.bullet}</td>
        <td class="num">${p.grain} gr</td>
        <td>${p.casing}</td>
        <td class="num">${p.rounds.toLocaleString()}</td>
        <td class="num t-cpr">${cents(p.cprNum)}</td>
        <td class="num">${priceBlock}</td>
        <td class="num"><span class="t-stock ${stockClass(p.stock)}">${stockLabel(p.stock)}</span></td>
        <td class="center">
          <button class="btn btn-primary t-buy add-to-cart" ${out ? "disabled" : ""}>${out ? "Notify" : "Add"}</button>
        </td>
      </tr>`;
  }).join("");
}

/* ---------- Cart counter (shared with homepage behavior) ---------- */
function wireCart() {
  const countEl = document.querySelector(".cart-count");
  let count = 0;
  document.body.addEventListener("click", e => {
    const btn = e.target.closest(".add-to-cart");
    if (!btn || btn.disabled) return;
    count += 1;
    if (countEl) countEl.textContent = count;
    const original = btn.textContent;
    btn.textContent = "✓";
    setTimeout(() => { btn.textContent = original; }, 1000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderCards();
  renderTable();
  wireCart();
});
