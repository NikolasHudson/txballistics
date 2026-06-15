/* Flash "✓ Added" on any add-to-cart button after a successful HTMX add. */
(function () {
  document.body.addEventListener("htmx:afterRequest", function (e) {
    const form = e.detail.elt;
    if (!e.detail.successful || !form.matches || !form.matches("form")) return;
    const btn = form.querySelector(".add-to-cart");
    if (!btn) return;
    if (btn.dataset.flashing) return;
    btn.dataset.flashing = "1";
    const original = btn.innerHTML;
    btn.innerHTML = "✓ Added";
    btn.classList.add("added");
    btn.disabled = true;
    setTimeout(function () {
      btn.innerHTML = original;
      btn.classList.remove("added");
      btn.disabled = false;
      delete btn.dataset.flashing;
    }, 1200);
  });
})();
