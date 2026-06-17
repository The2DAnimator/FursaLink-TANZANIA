/* Shared pagination renderer for listing pages (DRF PageNumberPagination). */
function renderPager(elId, data, onGo) {
  const el = document.getElementById(elId);
  if (!el) return;
  const pageSize = 20;
  const total = Math.ceil((data.count || 0) / pageSize);
  if (total <= 1) { el.innerHTML = ""; return; }
  const current = data.current || 1;
  let html = "";
  html += `<li class="page-item ${data.previous ? "" : "disabled"}"><a class="page-link" href="#">Prev</a></li>`;
  for (let p = 1; p <= total; p++) {
    if (total > 7 && Math.abs(p - current) > 2 && p !== 1 && p !== total) {
      if (Math.abs(p - current) === 3) html += `<li class="page-item disabled"><span class="page-link">…</span></li>`;
      continue;
    }
    html += `<li class="page-item ${p === current ? "active" : ""}"><a class="page-link" href="#" data-p="${p}">${p}</a></li>`;
  }
  html += `<li class="page-item ${data.next ? "" : "disabled"}"><a class="page-link" href="#">Next</a></li>`;
  el.innerHTML = html;
  el.querySelectorAll("a[data-p]").forEach((a) =>
    a.addEventListener("click", (e) => { e.preventDefault(); onGo(parseInt(a.dataset.p, 10)); }));
  const links = el.querySelectorAll("a.page-link");
  if (data.previous) links[0].addEventListener("click", (e) => { e.preventDefault(); onGo(current - 1); });
  if (data.next) links[links.length - 1].addEventListener("click", (e) => { e.preventDefault(); onGo(current + 1); });
}

/* DRF responses don't include the current page; track it via the caller. */
function withCurrent(data, page) { data.current = page; return data; }
