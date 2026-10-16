(() => {
  "use strict";

  const STORAGE_KEY = "medflow.portal.prototype.v1";
  const tenantNames = { northstar: "Northstar Billing", cedar: "Cedar Health Admin" };
  const $ = (id) => document.getElementById(id);
  const els = {
    tenant: $("tenantSelect"), table: $("claimsTable"), empty: $("emptyState"),
    total: $("metricTotal"), processing: $("metricProcessing"), review: $("metricReview"),
    accepted: $("metricAccepted"), navCount: $("navClaimCount"), summary: $("tableSummary"),
    search: $("searchInput"), filter: $("statusFilter"), modal: $("claimModal"),
    form: $("claimForm"), error: $("formError"), toast: $("toast")
  };
  let toastTimer;
  let claims = loadClaims();

  function seedClaims() {
    const now = new Date();
    const daysAgo = (n) => { const d = new Date(now); d.setDate(d.getDate() - n); return d.toISOString(); };
    return [
      {id:"CLM-1042",tenant:"northstar",clientRef:"DEMO-REF-218",submittedAt:daysAgo(0),serviceDate:"2026-10-08",amount:425.00,status:"Processing",fileName:"example-claim.pdf",key:"seed-1042"},
      {id:"CLM-1041",tenant:"northstar",clientRef:"DEMO-REF-217",submittedAt:daysAgo(1),serviceDate:"2026-10-07",amount:189.50,status:"Accepted",fileName:"synthetic-document.tif",key:"seed-1041"},
      {id:"CLM-1040",tenant:"northstar",clientRef:"DEMO-REF-216",submittedAt:daysAgo(2),serviceDate:"2026-10-06",amount:760.25,status:"Manual review",fileName:"sample-claim.pdf",key:"seed-1040"},
      {id:"CLM-1039",tenant:"northstar",clientRef:"DEMO-REF-215",submittedAt:daysAgo(3),serviceDate:"2026-10-05",amount:92.00,status:"Rejected",fileName:"demo-file.pdf",key:"seed-1039"},
      {id:"CLM-2042",tenant:"cedar",clientRef:"CEDAR-DEMO-09",submittedAt:daysAgo(0),serviceDate:"2026-10-09",amount:312.75,status:"Accepted",fileName:"cedar-example.pdf",key:"seed-2042"},
      {id:"CLM-2041",tenant:"cedar",clientRef:"CEDAR-DEMO-08",submittedAt:daysAgo(2),serviceDate:"2026-10-07",amount:540.00,status:"Processing",fileName:"cedar-sample.tif",key:"seed-2041"}
    ];
  }

  function loadClaims() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : seedClaims();
    } catch (_) {
      return seedClaims();
    }
  }
  function saveClaims() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(claims)); }
    catch (_) { showToast("Browser storage is unavailable; changes may not persist after refresh."); }
  }
  function currentTenant() { return els.tenant.value; }
  function tenantClaims() { return claims.filter(c => c.tenant === currentTenant()); }
  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  }
  function formatDate(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? "—" : new Intl.DateTimeFormat("en-US",{month:"short",day:"2-digit",year:"numeric"}).format(date);
  }
  function formatMoney(value) {
    return new Intl.NumberFormat("en-US",{style:"currency",currency:"USD"}).format(Number(value)||0);
  }
  function statusClass(status) {
    const allowedClasses = {
      "Processing": "processing",
      "Accepted": "accepted",
      "Manual review": "manual-review",
      "Rejected": "rejected"
    };
    return Object.prototype.hasOwnProperty.call(allowedClasses, status)
      ? allowedClasses[status]
      : "unknown";
  }
  function render() {
    const all = tenantClaims();
    const query = els.search.value.trim().toLowerCase();
    const filter = els.filter.value;
    const filtered = all.filter(c => (filter === "all" || c.status === filter) &&
      [c.id,c.clientRef,c.fileName,c.status].join(" ").toLowerCase().includes(query));
    els.total.textContent = all.length;
    els.processing.textContent = all.filter(c => c.status === "Processing").length;
    els.review.textContent = all.filter(c => c.status === "Manual review").length;
    els.accepted.textContent = all.filter(c => c.status === "Accepted").length;
    els.navCount.textContent = all.length;
    els.summary.textContent = `Showing ${filtered.length} of ${all.length} claim${all.length===1?"":"s"}`;
    els.table.innerHTML = filtered.map(c => `
      <tr>
        <td><div class="claim-cell"><div class="claim-doc">▤</div><div><div class="claim-id">${escapeHtml(c.id)}</div><div class="claim-type">Medical claim · demo</div></div></div></td>
        <td><span class="client-ref">${escapeHtml(c.clientRef)}</span></td>
        <td>${formatDate(c.submittedAt)}</td>
        <td><span class="amount">${formatMoney(c.amount)}</span></td>
        <td><span class="status-pill ${statusClass(c.status)}">${escapeHtml(c.status)}</span></td>
        <td><button class="row-action" data-claim-id="${escapeHtml(c.id)}" title="View demo details" aria-label="View ${escapeHtml(c.id)} details">···</button></td>
      </tr>`).join("");
    els.empty.hidden = filtered.length > 0;
  }
  function showToast(message) {
    clearTimeout(toastTimer);
    els.toast.textContent = message;
    els.toast.classList.add("show");
    toastTimer = setTimeout(() => els.toast.classList.remove("show"), 3200);
  }
  function openModal() {
    els.error.hidden = true;
    els.form.reset();
    $("serviceDate").value = new Date().toISOString().slice(0,10);
    els.modal.hidden = false;
    $("clientRef").focus();
  }
  function closeModal() {
    els.modal.hidden = true;
    $("newClaimTop").focus();
  }
  function createClaim(formData) {
    const tenant = currentTenant();
    const clientRef = String(formData.get("clientRef") || "").trim();
    const serviceDate = String(formData.get("serviceDate") || "");
    const amount = Number(formData.get("amount"));
    const outcome = String(formData.get("demoOutcome") || "Accepted");
    if (!clientRef || !serviceDate || !Number.isFinite(amount) || amount <= 0) {
      els.error.textContent = "Enter a client reference, service date, and a valid amount.";
      els.error.hidden = false;
      return;
    }
    const duplicate = tenantClaims().some(c => c.clientRef.toLowerCase() === clientRef.toLowerCase());
    if (duplicate) {
      els.error.textContent = "That client reference already exists in this demo workspace. Use a different synthetic reference.";
      els.error.hidden = false;
      return;
    }
    const file = $("documentFile").files && $("documentFile").files[0];
    const nextNumber = Math.max(1000, ...claims.map(c => Number((c.id.match(/\d+$/)||["1000"])[0]))) + 1;
    const id = `CLM-${nextNumber}`;
    const record = {
      id, tenant, clientRef, serviceDate, amount,
      submittedAt: new Date().toISOString(),
      status: "Processing",
      demoOutcome: outcome,
      fileName: file ? file.name : "No document selected",
      key: `demo-${cryptoRandomKey()}`
    };
    claims.unshift(record);
    saveClaims();
    render();
    closeModal();
    showToast(`${id} submitted in ${tenantNames[tenant]}. Processing is simulated.`);
    // Simulate eventual processing, without a network request.
    setTimeout(() => {
      const item = claims.find(c => c.id === id && c.tenant === tenant);
      if (!item || item.status !== "Processing") return;
      item.status = outcome;
      saveClaims();
      if (currentTenant() === tenant) render();
      showToast(`${id} demo processing complete: ${outcome}.`);
    }, 4500);
  }
  function cryptoRandomKey() {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }
  function showDetails(id) {
    const c = tenantClaims().find(item => item.id === id);
    if (!c) return;
    const text = `${c.id}\nWorkspace: ${tenantNames[c.tenant]}\nClient reference: ${c.clientRef}\nService date: ${c.serviceDate || "—"}\nAmount: ${formatMoney(c.amount)}\nStatus: ${c.status}\nDocument: ${c.fileName}\nIdempotency key: ${c.key}\n\nDemo only. This record is stored in browser local storage; no backend is connected.`;
    window.alert(text);
  }

  $("newClaimTop").addEventListener("click", openModal);
  $("emptySubmit").addEventListener("click", openModal);
  $("closeModal").addEventListener("click", closeModal);
  $("cancelModal").addEventListener("click", closeModal);
  $("dismissBanner").addEventListener("click", () => $("dismissBanner").closest(".demo-banner").remove());
  els.form.addEventListener("submit", event => {
    event.preventDefault();
    createClaim(new FormData(els.form));
  });
  els.tenant.addEventListener("change", () => {
    document.querySelector(".breadcrumb strong").textContent = "Overview";
    render();
    showToast(`Switched to ${tenantNames[currentTenant()]}. Demo records are shown per workspace.`);
  });
  els.search.addEventListener("input", render);
  els.filter.addEventListener("change", render);
  els.table.addEventListener("click", event => {
    const button = event.target.closest("[data-claim-id]");
    if (button) showDetails(button.dataset.claimId);
  });
  els.modal.addEventListener("click", event => { if (event.target === els.modal) closeModal(); });
  document.addEventListener("keydown", event => { if (event.key === "Escape" && !els.modal.hidden) closeModal(); });
  document.querySelectorAll('.nav-link[href="#submit"]').forEach(link => link.addEventListener("click", event => { event.preventDefault(); openModal(); }));
  document.querySelectorAll('.nav-link[href="#claims"]').forEach(link => link.addEventListener("click", event => { event.preventDefault(); $("claims").scrollIntoView({behavior:"smooth",block:"start"}); }));
  document.querySelectorAll('.nav-link[href="#overview"]').forEach(link => link.addEventListener("click", event => { event.preventDefault(); $("overview").scrollIntoView({behavior:"smooth",block:"start"}); }));

  render();
})();
