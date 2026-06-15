/* TX Ballistics — homepage testimonials rotator (server-rendered data) */
(function () {
  const wrap = document.getElementById("testimonials");
  const dataEl = document.getElementById("quotes-data");
  if (!wrap || !dataEl) return;

  let quotes;
  try {
    quotes = JSON.parse(dataEl.textContent);
  } catch (e) {
    return;
  }
  if (!quotes.length) return;

  let i = 0;
  function render() {
    const q = quotes[i];
    wrap.innerHTML = `
      <div class="quote-stars">★★★★★</div>
      <p class="quote">"${q.text}"<span class="quote-author">— ${q.who}</span></p>
      <div class="quote-dots">
        ${quotes.map((_, idx) => `<button class="${idx === i ? "active" : ""}" data-i="${idx}" aria-label="Quote ${idx + 1}"></button>`).join("")}
      </div>`;
  }
  wrap.addEventListener("click", (e) => {
    const dot = e.target.closest("[data-i]");
    if (!dot) return;
    i = Number(dot.dataset.i);
    render();
  });
  render();
  setInterval(() => { i = (i + 1) % quotes.length; render(); }, 5000);
})();
