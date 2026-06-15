/* ===========================================================
   TX Ballistics — Category listing (data-driven)
   Reads ?cat= and optional ?caliber= from the URL and renders
   the real catalog: sidebar of calibers, usage filter, sort,
   and a card/table view toggle.
   =========================================================== */

const state = {
  cat: TXB.param("cat") || TXB.categories()[0],
  caliber: TXB.param("caliber") || null,
  view: "cards",
  sort: "cpr",
  usages: new Set(), // empty = show all
};

/* ---------- helpers ---------- */
function baseSet() {
  let items = TXB.byCategory(state.cat);
  if (state.caliber) items = items.filter((p) => p.caliber === state.caliber);
  return items;
}

// Usage filter options come from whatever's actually in this caliber/category.
function usageOptions(items) {
  const out = [];
  items.forEach((p) => {
    if (p.usage && !out.includes(p.usage)) out.push(p.usage);
  });
  return out.sort();
}

function applyFilterSort(items) {
  let out = items;
  if (state.usages.size) out = out.filter((p) => state.usages.has(p.usage));
  const sorters = {
    cpr: (a, b) => a.costPerRound - b.costPerRound,
    "price-asc": (a, b) => a.cost - b.cost,
    "price-desc": (a, b) => b.cost - a.cost,
    grain: (a, b) => (a.grain || 0) - (b.grain || 0),
    caliber: (a, b) => a.caliber.localeCompare(b.caliber),
  };
  return [...out].sort(sorters[state.sort] || sorters.cpr);
}

/* ---------- renderers ---------- */
function renderBreadcrumb() {
  const el = document.getElementById("breadcrumb");
  el.innerHTML =
    `<a href="index.html">Home</a><span class="sep">›</span>` +
    `<a href="${TXB.categoryHref(state.cat)}">${state.cat} Ammo</a>` +
    (state.caliber
      ? `<span class="sep">›</span><span class="current">${state.caliber}</span>`
      : `<span class="sep">›</span><span class="current">All ${state.cat}</span>`);
}

function renderHeading() {
  const title = state.caliber ? `${state.caliber} Ammo` : `${state.cat} Ammo`;
  document.getElementById("cat-title").textContent = title;
  document.getElementById("cat-intro").textContent = state.caliber
    ? `In-stock ${state.caliber} loads, ready for local pickup in Central Texas. Compare grain, box count, and cost per round.`
    : `Every ${state.cat.toLowerCase()} caliber we carry — reserve online and pick it up at our Central Texas counter.`;
  document.title = `${title} — TX Ballistics`;
}

function renderSidebar() {
  const aside = document.getElementById("cat-sidebar");
  const cals = TXB.calibersFor(state.cat);
  const others = TXB.categories().filter((c) => c !== state.cat);
  const usages = usageOptions(baseSet());

  aside.innerHTML = `
    <div class="side-block">
      <div class="side-head">${state.cat} Ammo</div>
      <ul class="side-list">
        <li class="${!state.caliber ? "active" : ""}">
          <a href="${TXB.categoryHref(state.cat)}">All ${state.cat} <span class="count">${TXB.byCategory(state.cat).length}</span></a>
        </li>
        ${cals
          .map(
            (c) => `<li class="${state.caliber === c.caliber ? "active" : ""}">
              <a href="${TXB.categoryHref(state.cat, c.caliber)}">${c.caliber} <span class="count">${c.count}</span></a>
            </li>`
          )
          .join("")}
      </ul>
    </div>
    ${
      others.length
        ? `<div class="side-block">
            <div class="side-head">More Categories</div>
            <ul class="side-list">
              ${others.map((c) => `<li><a href="${TXB.categoryHref(c)}">${c} Ammo</a></li>`).join("")}
            </ul>
          </div>`
        : ""
    }
    ${
      usages.length > 1
        ? `<div class="side-block">
            <div class="side-head">Best For</div>
            <div class="filter-group" id="usage-filter">
              ${usages
                .map(
                  (u) =>
                    `<label><input type="checkbox" value="${u}" ${
                      state.usages.has(u) ? "checked" : ""
                    } /> ${u}</label>`
                )
                .join("")}
            </div>
          </div>`
        : ""
    }`;

  const filter = document.getElementById("usage-filter");
  if (filter) {
    filter.addEventListener("change", (e) => {
      const cb = e.target.closest("input[type=checkbox]");
      if (!cb) return;
      if (cb.checked) state.usages.add(cb.value);
      else state.usages.delete(cb.value);
      renderListing();
    });
  }
}

function renderCards(items) {
  document.getElementById("cat-cards").innerHTML = items.map(TXB.productCard).join("");
}

function renderTable(items) {
  document.getElementById("cat-table").innerHTML = items
    .map(
      (p) => `
      <tr>
        <td>
          <div class="tcell-product">
            <a class="tcell-thumb" href="${TXB.productHref(p)}">${p.calShort || p.caliber}</a>
            <a class="tcell-title" href="${TXB.productHref(p)}">${p.description || p.name}</a>
          </div>
        </td>
        <td>${p.caliber}</td>
        <td class="num">${p.grain ? p.grain + " gr" : "—"}</td>
        <td>${p.usage || "—"}</td>
        <td class="num">${p.roundsPerBox}</td>
        <td class="num t-cpr">${TXB.cents(p.costPerRound)}</td>
        <td class="num"><span class="t-price">${TXB.money(p.cost)}</span></td>
        <td class="center">
          <button class="btn btn-primary t-buy add-to-cart" data-id="${p.id}">Add</button>
        </td>
      </tr>`
    )
    .join("");
}

function renderListing() {
  const total = baseSet().length;
  const items = applyFilterSort(baseSet());
  document.getElementById("result-count").innerHTML =
    `Showing <strong>${items.length}</strong> of ${total} in stock`;
  renderCards(items);
  renderTable(items);

  const cards = document.getElementById("cat-cards");
  const table = document.getElementById("cat-table-wrap");
  const isCards = state.view === "cards";
  cards.hidden = !isCards;
  table.hidden = isCards;
  document.querySelectorAll(".view-toggle [data-view]").forEach((a) => {
    a.classList.toggle("active", a.dataset.view === state.view);
  });
}

/* ---------- wiring ---------- */
function wireToolbar() {
  document.querySelectorAll(".view-toggle [data-view]").forEach((a) => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      state.view = a.dataset.view;
      renderListing();
    });
  });
  const sort = document.getElementById("sort-select");
  sort.value = state.sort;
  sort.addEventListener("change", () => {
    state.sort = sort.value;
    renderListing();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderBreadcrumb();
  renderHeading();
  renderSidebar();
  wireToolbar();
  renderListing();
});
