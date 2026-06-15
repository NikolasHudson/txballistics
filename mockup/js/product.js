/* ===========================================================
   TX Ballistics — Product Detail page (data-driven)
   Reads ?id= from the URL and renders the real product from
   window.PRODUCTS. Quantity stepper updates the running total.
   =========================================================== */

const PRODUCT = TXB.findProduct(TXB.param("id"));

function show(id) {
  const el = document.getElementById(id);
  if (el) el.hidden = false;
}

function renderProduct(p) {
  document.title = `${TXB.productTitle(p)} | TX Ballistics`;
  document.getElementById("gallery-main-label").textContent = p.calShort || p.caliber;

  // Breadcrumb
  document.getElementById("breadcrumb").innerHTML =
    `<a href="index.html">Home</a><span class="sep">›</span>` +
    `<a href="${TXB.categoryHref(p.category)}">${p.category} Ammo</a><span class="sep">›</span>` +
    `<a href="${TXB.categoryHref(p.category, p.caliber)}">${p.caliber}</a><span class="sep">›</span>` +
    `<span class="current">${p.description || p.name}</span>`;

  // Buy box
  document.getElementById("p-title").textContent = TXB.productTitle(p);
  document.getElementById("p-usage").textContent = p.usage ? `Best for: ${p.usage}` : "";
  document.getElementById("p-price").textContent = TXB.money(p.cost);
  document.getElementById("p-rounds-box").textContent = `${p.roundsPerBox}`;
  document.getElementById("p-cpr").textContent = `${TXB.cents(p.costPerRound)} per round`;

  // Quick specs (real fields only)
  document.getElementById("quick-specs").innerHTML = [
    ["Caliber", p.caliber],
    p.grain ? ["Bullet Weight", `${p.grain} grain`] : null,
    ["Rounds / Box", `${p.roundsPerBox}`],
    ["Cost / Round", TXB.cents(p.costPerRound)],
    ["Best For", p.usage || "—"],
    ["Category", `${p.category} ammo`],
  ]
    .filter(Boolean)
    .map(([k, v]) => `<div><span class="k">${k}</span><span class="v">${v}</span></div>`)
    .join("");

  // Description
  document.getElementById("p-description").textContent =
    `${TXB.productTitle(p)} — ${p.roundsPerBox} rounds per box at ${TXB.money(p.cost)} ` +
    `(${TXB.cents(p.costPerRound)} per round), suited for ${(p.usage || "general use").toLowerCase()}.`;

  // Specifications table
  document.getElementById("spec-table").innerHTML = [
    ["Caliber", p.caliber],
    p.grain ? ["Bullet Weight", `${p.grain} grain`] : null,
    ["Load", p.description || p.name],
    ["Rounds Per Box", `${p.roundsPerBox}`],
    ["Box Price", TXB.money(p.cost)],
    ["Cost Per Round", TXB.cents(p.costPerRound)],
    ["Best For", p.usage || "—"],
    ["Category", `${p.category} ammo`],
  ]
    .filter(Boolean)
    .map(([k, v]) => `<tr><td class="k">${k}</td><td>${v}</td></tr>`)
    .join("");

  // Related: same caliber, cheapest per round first
  const related = TXB.PRODUCTS.filter((x) => x.caliber === p.caliber && x.id !== p.id)
    .sort((a, b) => a.costPerRound - b.costPerRound)
    .slice(0, 4);
  document.getElementById("related-caliber").textContent = p.caliber;
  document.getElementById("related-grid").innerHTML = related
    .map(
      (r) => `
      <a href="${TXB.productHref(r)}" class="related-card">
        <div class="rimg">${r.calShort || r.caliber}</div>
        <h3>${r.description || r.name}</h3>
        <div class="rprice">${TXB.money(r.cost)} · ${TXB.cents(r.costPerRound)}/rd</div>
        <span class="btn btn-primary btn-block add-to-cart" data-id="${r.id}">Add to Cart</span>
      </a>`
    )
    .join("");

  show("product-top");
  show("description-section");
  show("spec-section");
  if (related.length) show("related-section");
}

/* ---------- Quantity stepper + live total ---------- */
function wireQty(p) {
  const input = document.getElementById("qty");
  const minus = document.getElementById("qty-minus");
  const plus = document.getElementById("qty-plus");
  const totalEl = document.getElementById("buy-total");
  const roundsEl = document.getElementById("buy-rounds");
  if (!input) return;

  const clamp = (n) => Math.max(1, Math.min(99, n));
  function update() {
    const q = clamp(parseInt(input.value, 10) || 1);
    input.value = q;
    totalEl.textContent = TXB.money(q * p.cost);
    roundsEl.textContent = (q * p.roundsPerBox).toLocaleString() + " rounds";
  }
  minus.addEventListener("click", () => {
    input.value = clamp((parseInt(input.value, 10) || 1) - 1);
    update();
  });
  plus.addEventListener("click", () => {
    input.value = clamp((parseInt(input.value, 10) || 1) + 1);
    update();
  });
  input.addEventListener("input", update);
  update();
}

document.addEventListener("DOMContentLoaded", () => {
  if (!PRODUCT) {
    show("not-found");
    return;
  }
  renderProduct(PRODUCT);
  wireQty(PRODUCT);
});
