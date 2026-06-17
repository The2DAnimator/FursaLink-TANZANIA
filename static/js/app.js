/* Shared UI helpers: nav auth state, formatting, rendering utilities. */
(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const authed = window.FL && FL.isAuthenticated();
    document.querySelectorAll('[data-auth="in"]').forEach((el) =>
      el.classList.toggle("d-none", !authed)
    );
    document.querySelectorAll('[data-auth="out"]').forEach((el) =>
      el.classList.toggle("d-none", !!authed)
    );
    const logout = document.getElementById("logout-link");
    if (logout) logout.addEventListener("click", (e) => { e.preventDefault(); FL.logout(); });
  });

  window.FLUI = {
    money(amount, currency = "TZS") {
      if (amount == null) return "—";
      return `${currency} ${Number(amount).toLocaleString()}`;
    },
    escape(str) {
      const d = document.createElement("div");
      d.textContent = str ?? "";
      return d.innerHTML;
    },
    qs(params) {
      const usp = new URLSearchParams();
      Object.entries(params).forEach(([k, v]) => { if (v) usp.set(k, v); });
      const s = usp.toString();
      return s ? `?${s}` : "";
    },
    spinner(target) {
      target.innerHTML =
        '<div class="text-center py-5"><div class="spinner-border text-success"></div></div>';
    },
    empty(target, msg = "No results found.") {
      target.innerHTML = `<div class="alert alert-light border text-center my-4">${msg}</div>`;
    },
    toast(msg, type = "success") {
      const wrap = document.createElement("div");
      wrap.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3 shadow`;
      wrap.style.zIndex = 1080;
      wrap.textContent = msg;
      document.body.appendChild(wrap);
      setTimeout(() => wrap.remove(), 3000);
    },
  };
})();
