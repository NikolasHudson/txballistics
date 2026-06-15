/* ===========================================================
   TX Ballistics — Sign In / Register tab switching
   =========================================================== */

function showAuth(name) {
  document.querySelectorAll(".auth-tab").forEach(t =>
    t.classList.toggle("active", t.dataset.auth === name));
  document.querySelectorAll(".auth-form").forEach(f =>
    f.classList.toggle("active", f.id === "auth-" + name));

  // Bottom switch prompt flips to the opposite action
  const sw = document.getElementById("auth-switch");
  if (sw) {
    sw.innerHTML = name === "signin"
      ? 'New to TX Ballistics? <button type="button" data-auth="register">Create an account →</button>'
      : 'Already have an account? <button type="button" data-auth="signin">Sign in →</button>';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("click", e => {
    const trigger = e.target.closest("[data-auth]");
    if (!trigger) return;
    showAuth(trigger.dataset.auth);
  });
});
