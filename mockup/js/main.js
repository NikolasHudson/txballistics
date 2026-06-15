/* ===========================================================
   TX Ballistics — Homepage
   Renders the hero "deal" card, category grid, and featured
   specials from the real catalog (window.PRODUCTS via TXB).
   =========================================================== */

/* ---------- Featured specials: cheapest-per-round pick from a
   spread of popular calibers, so the row shows real variety. ---------- */
function pickFeatured() {
  const wanted = [
    "9mm",
    "223 Remington",
    "308 Winchester",
    "45 ACP",
    "6.5 Creedmoor",
    "300 Blackout",
  ];
  const picks = [];
  wanted.forEach((cal) => {
    const inCal = TXB.PRODUCTS.filter((p) => p.caliber === cal);
    if (!inCal.length) return;
    inCal.sort((a, b) => a.costPerRound - b.costPerRound);
    picks.push(inCal[0]);
  });
  return picks;
}

function renderFeatured() {
  const wrap = document.getElementById("product-list");
  if (!wrap) return;
  wrap.innerHTML = pickFeatured().map(TXB.productCard).join("");
}

/* ---------- Hero deal card: lowest cost-per-round in the catalog ---------- */
function renderHeroDeal() {
  const card = document.getElementById("hero-deal");
  if (!card) return;
  const p = [...TXB.PRODUCTS].sort((a, b) => a.costPerRound - b.costPerRound)[0];
  if (!p) return;
  card.innerHTML = `
    <span class="stock-tag">BEST VALUE</span>
    <a class="hero-card-img" href="${TXB.productHref(p)}">${p.calShort || p.caliber}</a>
    <h3><a href="${TXB.productHref(p)}">${TXB.productTitle(p)}</a></h3>
    <p class="hero-card-brand">${p.roundsPerBox} rounds / box · ${p.usage}</p>
    <div class="hero-card-price">
      <span class="price-now">${TXB.money(p.cost)}</span>
    </div>
    <p class="cpr">${TXB.cents(p.costPerRound)} / round</p>
    <button class="btn btn-primary btn-block add-to-cart" data-id="${p.id}">Add to Cart</button>`;
}

/* ---------- Category grid: one card per real category ---------- */
function renderCategoryGrid() {
  const wrap = document.getElementById("category-grid");
  if (!wrap) return;
  wrap.innerHTML = TXB.categories()
    .map((c) => {
      const cals = TXB.calibersFor(c).slice(0, 4).map((x) => x.caliber).join(" · ");
      const total = TXB.byCategory(c).length;
      return `
        <a href="${TXB.categoryHref(c)}" class="cat-card">
          <h3>${c}<br />Ammo</h3>
          <p>${cals}</p>
          <span class="cat-count">${total} loads in stock</span>
        </a>`;
    })
    .join("");
}

document.addEventListener("DOMContentLoaded", () => {
  renderHeroDeal();
  renderCategoryGrid();
  renderFeatured();
});
