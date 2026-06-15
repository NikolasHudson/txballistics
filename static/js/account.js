/* ===========================================================
   TX Ballistics — Account page interactivity
   - Sidebar tab switching
   - "Add to cart" feedback on saved items
   =========================================================== */

function showTab(name) {
  document.querySelectorAll(".acct-panel").forEach(p =>
    p.classList.toggle("active", p.id === "tab-" + name));
  document.querySelectorAll(".acct-link[data-tab]").forEach(b =>
    b.classList.toggle("active", b.dataset.tab === name));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
  // Sidebar tabs
  document.querySelectorAll(".acct-link[data-tab]").forEach(btn =>
    btn.addEventListener("click", () => showTab(btn.dataset.tab)));

  // Inline jump links (e.g. "View Order" on dashboard)
  document.querySelectorAll("[data-tab-jump]").forEach(el =>
    el.addEventListener("click", e => { e.preventDefault(); showTab(el.dataset.tabJump); }));

  // Save buttons feedback
  document.querySelectorAll(".acct-save").forEach(btn =>
    btn.addEventListener("click", () => {
      const original = btn.textContent;
      btn.textContent = "✓ Saved!";
      btn.disabled = true;
      setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 1400);
    }));

  // Add-to-cart feedback + header badge
  const badge = document.querySelector(".cart-count");
  let count = badge ? parseInt(badge.textContent, 10) || 0 : 0;
  document.body.addEventListener("click", e => {
    const btn = e.target.closest(".add-to-cart");
    if (!btn) return;
    count += 1;
    if (badge) badge.textContent = count;
    const original = btn.textContent;
    btn.textContent = "✓ Added!";
    btn.disabled = true;
    setTimeout(() => { btn.textContent = original; btn.disabled = false; }, 1200);
  });
});
