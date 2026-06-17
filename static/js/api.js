/* Lightweight REST API client for FursaLink Tanzania.
 * Handles JWT storage, auto-refresh and JSON/form requests via the Fetch API.
 */
(function (window) {
  const BASE = "/api/v1";
  const ACCESS = "fl_access";
  const REFRESH = "fl_refresh";

  const tokens = {
    get access() { return localStorage.getItem(ACCESS); },
    get refresh() { return localStorage.getItem(REFRESH); },
    set({ access, refresh }) {
      if (access) localStorage.setItem(ACCESS, access);
      if (refresh) localStorage.setItem(REFRESH, refresh);
    },
    clear() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH); },
  };

  function isAuthenticated() { return !!tokens.access; }

  async function rawRequest(path, { method = "GET", body, auth = true, isForm = false } = {}) {
    const headers = {};
    if (!isForm) headers["Content-Type"] = "application/json";
    if (auth && tokens.access) headers["Authorization"] = `Bearer ${tokens.access}`;
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
    });
    return res;
  }

  async function refreshAccess() {
    if (!tokens.refresh) return false;
    const res = await rawRequest("/auth/refresh/", {
      method: "POST", auth: false, body: { refresh: tokens.refresh },
    });
    if (res.ok) { tokens.set(await res.json()); return true; }
    tokens.clear();
    return false;
  }

  async function request(path, opts = {}) {
    let res = await rawRequest(path, opts);
    if (res.status === 401 && opts.auth !== false && tokens.refresh) {
      if (await refreshAccess()) res = await rawRequest(path, opts);
    }
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) throw { status: res.status, data };
    return data;
  }

  const api = {
    tokens,
    isAuthenticated,
    request,
    get: (p) => request(p),
    post: (p, body, opts) => request(p, { method: "POST", body, ...opts }),
    patch: (p, body) => request(p, { method: "PATCH", body }),
    del: (p) => request(p, { method: "DELETE" }),
    async login(email, password) {
      const data = await request("/auth/login/", {
        method: "POST", auth: false, body: { email, password },
      });
      tokens.set(data);
      return data;
    },
    logout() { tokens.clear(); window.location.href = "/"; },
    me: () => request("/me/"),
  };

  window.FL = api;
})(window);
