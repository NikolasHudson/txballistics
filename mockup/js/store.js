/* ===========================================================
   TX Ballistics — shared storefront helpers
   Loaded on every page AFTER data.js, BEFORE the page script.
   Everything here works off the real catalog in window.PRODUCTS.
   =========================================================== */
(function () {
  const PRODUCTS = window.PRODUCTS || [];

  /* ---------- formatting ---------- */
  const money = (n) => "$" + Number(n).toFixed(2);
  const cents = (n) => {
    const c = Math.round(Number(n) * 100);
    return c >= 100 ? "$" + (c / 100).toFixed(2) : c + "¢";
  };

  // Product names already read like "9mm - 124gn Hybrid - HP". Present them as
  // "9mm — 124gn Hybrid - HP" for a slightly cleaner headline.
  const productTitle = (p) => {
    const tail = p.description || p.name;
    return `${p.caliber} — ${tail}`;
  };

  const findProduct = (id) => PRODUCTS.find((p) => p.id === id) || null;

  const byCategory = (cat) =>
    PRODUCTS.filter((p) => p.category.toLowerCase() === String(cat).toLowerCase());

  // Ordered list of calibers within a category, with product counts.
  const calibersFor = (cat) => {
    const out = [];
    const seen = new Map();
    byCategory(cat).forEach((p) => {
      if (!seen.has(p.caliber)) {
        seen.set(p.caliber, out.length);
        out.push({ caliber: p.caliber, count: 1 });
      } else {
        out[seen.get(p.caliber)].count += 1;
      }
    });
    return out;
  };

  const categories = () => {
    const out = [];
    PRODUCTS.forEach((p) => {
      if (!out.includes(p.category)) out.push(p.category);
    });
    return out;
  };

  const productHref = (p) => `product.html?id=${encodeURIComponent(p.id)}`;
  const categoryHref = (cat, caliber) =>
    `category.html?cat=${encodeURIComponent(cat)}` +
    (caliber ? `&caliber=${encodeURIComponent(caliber)}` : "");

  const param = (name) => new URLSearchParams(location.search).get(name);

  /* ---------- shared product card markup ---------- */
  function productCard(p) {
    return `
      <article class="product-card">
        ${p.usage ? `<span class="stock-badge usage">${p.usage}</span>` : ""}
        <a class="pc-img" href="${productHref(p)}">${p.calShort || p.caliber}</a>
        <div class="pc-body">
          <h3><a href="${productHref(p)}">${productTitle(p)}</a></h3>
          <ul class="pc-specs">
            ${p.grain ? `<li>${p.grain} grain</li>` : ""}
            <li>${p.roundsPerBox} rounds / box</li>
            <li>${p.caliber}</li>
            <li>${p.category}</li>
          </ul>
        </div>
        <div class="pc-buy">
          <div><span class="pc-price">${money(p.cost)}</span></div>
          <span class="pc-cpr">${cents(p.costPerRound)} / round</span>
          <button class="btn btn-primary btn-block add-to-cart" data-id="${p.id}">Add to Cart</button>
        </div>
      </article>`;
  }

  /* ---------- cart counter (visual; persists across pages) ---------- */
  function cartCount() {
    return Number(localStorage.getItem("txb_cart") || "0");
  }
  function wireCart() {
    const els = document.querySelectorAll(".cart-count");
    els.forEach((el) => (el.textContent = cartCount()));
    document.body.addEventListener("click", (e) => {
      const btn = e.target.closest(".add-to-cart");
      if (!btn || btn.disabled) return;
      e.preventDefault();
      localStorage.setItem("txb_cart", String(cartCount() + 1));
      document.querySelectorAll(".cart-count").forEach((el) => (el.textContent = cartCount()));
      const original = btn.textContent;
      btn.textContent = "✓ Added!";
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = original;
        btn.disabled = false;
      }, 1100);
    });
  }

  /* ---------- shared nav: link categories to real pages ---------- */
  function wireNav() {
    document.querySelectorAll("[data-nav-categories]").forEach((ul) => {
      const items = categories()
        .map((c) => `<li><a href="${categoryHref(c)}">${c}</a></li>`)
        .join("");
      ul.innerHTML =
        items +
        `<li><a href="index.html#specials" class="nav-special">Specials</a></li>` +
        `<li><a href="about.html">About</a></li>`;
    });
  }

  window.TXB = {
    PRODUCTS,
    money,
    cents,
    productTitle,
    productCard,
    findProduct,
    byCategory,
    calibersFor,
    categories,
    productHref,
    categoryHref,
    param,
    wireCart,
    wireNav,
  };

  document.addEventListener("DOMContentLoaded", () => {
    wireNav();
    wireCart();
  });
})();
