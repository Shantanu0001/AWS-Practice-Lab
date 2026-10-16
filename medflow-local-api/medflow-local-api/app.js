(() => {
  "use strict";

  const tenantNames = {
    northstar: "Northstar Billing",
    cedar: "Cedar Health Admin",
  };

  const $ = (id) => document.getElementById(id);

  const els = {
    tenant: $("tenantSelect"),
    table: $("claimsTable"),
    empty: $("emptyState"),
    total: $("metricTotal"),
    processing: $("metricProcessing"),
    review: $("metricReview"),
    accepted: $("metricAccepted"),
    navCount: $("navClaimCount"),
    summary: $("tableSummary"),
    loadMore: $("loadMoreClaims"),
    search: $("searchInput"),
    filter: $("statusFilter"),
    modal: $("claimModal"),
    form: $("claimForm"),
    error: $("formError"),
    toast: $("toast"),
  };

  let toastTimer;
  let claims = [];
  let busy = false;
  let nextToken = null;
  let loadingMore = false;
  let loadGeneration = 0;

  const apiStatus = {
    PROCESSING: "Processing",
    ACCEPTED: "Accepted",
    MANUAL_REVIEW: "Manual review",
    REJECTED: "Rejected",
  };

  function currentTenant() {
    return els.tenant.value;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[ch]);
  }

  function formatDate(value) {
    const d = new Date(value);

    return Number.isNaN(d.getTime())
      ? "—"
      : new Intl.DateTimeFormat("en-US", {
          month: "short",
          day: "2-digit",
          year: "numeric",
        }).format(d);
  }

  function formatMoney(value) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(Number(value) || 0);
  }

  function statusLabel(status) {
    return apiStatus[status] || status;
  }

  function statusClass(status) {
    return statusLabel(status).toLowerCase().replace(/\s+/g, "-");
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    els.toast.textContent = message;
    els.toast.classList.add("show");

    toastTimer = setTimeout(
      () => els.toast.classList.remove("show"),
      3500
    );
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-Demo-Tenant": currentTenant(),
        ...(options.headers || {}),
      },
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      const err = payload || {};

      throw new Error(
        `${err.message || `Request failed (${response.status})`} ` +
        `[${err.code || "HTTP_ERROR"}; request ${err.requestId || "n/a"}]`
      );
    }

    return payload;
  }

  async function loadClaims(silent = false) {
    const generation = ++loadGeneration;
    const tenant = currentTenant();

    nextToken = null;
    loadingMore = false;

    els.loadMore.hidden = true;
    els.loadMore.disabled = false;
    els.loadMore.textContent = "Load more claims";

    try {
      const result = await api("/v1/claims?limit=100");

      // Ignore stale responses after a refresh or tenant switch.
      if (
        generation !== loadGeneration ||
        tenant !== currentTenant()
      ) {
        return;
      }

      claims = result.items || [];
      nextToken = result.nextToken || null;

      render();
      updatePagination();

      if (!silent) {
        showToast(
          `Loaded ${claims.length} claims from the local mock API.`
        );
      }
    } catch (error) {
      if (generation !== loadGeneration) return;

      showError(error.message);

      if (!silent) {
        showToast("Could not load claims. Is server.py running?");
      }
    }
  }

  function updatePagination() {
    els.loadMore.hidden = !nextToken;
    els.loadMore.disabled = loadingMore;

    els.loadMore.textContent = loadingMore
      ? "Loading…"
      : "Load more claims";
  }

  async function loadMoreClaims() {
    if (!nextToken || loadingMore) return;

    const token = nextToken;
    const tenant = currentTenant();
    const generation = loadGeneration;

    loadingMore = true;
    updatePagination();

    try {
      const result = await api(
        `/v1/claims?limit=100&nextToken=${encodeURIComponent(token)}`
      );

      // Do not append results from a previous tenant or refresh.
      if (
        generation !== loadGeneration ||
        tenant !== currentTenant()
      ) {
        return;
      }

      const existingIds = new Set(
        claims.map((claim) => claim.claimId)
      );

      for (const claim of result.items || []) {
        if (!existingIds.has(claim.claimId)) {
          claims.push(claim);
          existingIds.add(claim.claimId);
        }
      }

      nextToken = result.nextToken || null;

      render();
    } catch (error) {
      if (generation === loadGeneration) {
        showToast(`Could not load more claims: ${error.message}`);
      }
    } finally {
      if (generation === loadGeneration) {
        loadingMore = false;
        updatePagination();
      }
    }
  }

  function render() {
    const all = claims;
    const query = els.search.value.trim().toLowerCase();
    const filter = els.filter.value;

    const filtered = all.filter((c) => {
      const matchesStatus =
        filter === "all" || statusLabel(c.status) === filter;

      const searchable = [
        c.claimId,
        c.clientReference,
        c.documentFileName,
        statusLabel(c.status),
      ].join(" ").toLowerCase();

      return matchesStatus && searchable.includes(query);
    });

    els.total.textContent = all.length;

    els.processing.textContent = all.filter(
      (c) => c.status === "PROCESSING"
    ).length;

    els.review.textContent = all.filter(
      (c) => c.status === "MANUAL_REVIEW"
    ).length;

    els.accepted.textContent = all.filter(
      (c) => c.status === "ACCEPTED"
    ).length;

    els.navCount.textContent = all.length;

    els.summary.textContent =
      `Showing ${filtered.length} of ${all.length} claim` +
      `${all.length === 1 ? "" : "s"}`;

    els.table.innerHTML = filtered.map((c) => `
      <tr>
        <td>
          <div class="claim-cell">
            <div class="claim-doc">▤</div>
            <div>
              <div class="claim-id">${escapeHtml(c.claimId)}</div>
              <div class="claim-type">Medical claim · demo</div>
            </div>
          </div>
        </td>
        <td>
          <span class="client-ref">
            ${escapeHtml(c.clientReference)}
          </span>
        </td>
        <td>${formatDate(c.submittedAt)}</td>
        <td>
          <span class="amount">${formatMoney(c.amount)}</span>
        </td>
        <td>
          <span class="status-pill ${statusClass(c.status)}">
            ${escapeHtml(statusLabel(c.status))}
          </span>
        </td>
        <td>
          <button
            class="row-action"
            data-claim-id="${escapeHtml(c.claimId)}"
            title="View demo details"
            aria-label="View ${escapeHtml(c.claimId)} details"
          >···</button>
        </td>
      </tr>
    `).join("");

    els.empty.hidden = filtered.length > 0;
  }

  function showError(message) {
    els.error.textContent = message;
    els.error.hidden = false;
  }

  function openModal() {
    els.error.hidden = true;
    els.form.reset();

    $("serviceDate").value = new Date()
      .toISOString()
      .slice(0, 10);

    els.modal.hidden = false;
    $("clientRef").focus();
  }

  function closeModal() {
    els.modal.hidden = true;
    $("newClaimTop").focus();
  }

  function randomKey() {
    return window.crypto?.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  async function createClaim(data) {
    const clientReference = String(
      data.get("clientRef") || ""
    ).trim();

    const serviceDate = String(data.get("serviceDate") || "");
    const amount = Number(data.get("amount"));

    if (
      !clientReference ||
      !serviceDate ||
      !Number.isFinite(amount) ||
      amount <= 0
    ) {
      showError(
        "Enter a client reference, service date, and valid positive amount."
      );
      return;
    }

    const file = $("documentFile").files?.[0];

    const body = {
      clientReference,
      serviceDate,
      amount,
    };

    if (file) {
      const contentType =
        file.type === "image/tiff" ||
        /\.tiff?$/i.test(file.name)
          ? "image/tiff"
          : "application/pdf";

      body.document = {
        fileName: file.name,
        contentType,
        sizeBytes: file.size,
      };
    }

    // Metadata only; no file bytes are uploaded.
    const submit = els.form.querySelector('button[type="submit"]');

    submit.disabled = true;
    submit.textContent = "Submitting…";
    els.error.hidden = true;

    try {
      const result = await api("/v1/claims", {
        method: "POST",
        headers: {
          "Idempotency-Key": randomKey(),
        },
        body: JSON.stringify(body),
      });

      closeModal();
      await loadClaims(true);

      showToast(
        `${result.claimId} accepted by mock API. ` +
        "Status is PROCESSING; refresh will show the eventual outcome."
      );

      pollClaim(result.claimId, 0);
    } catch (error) {
      showError(error.message);
    } finally {
      submit.disabled = false;
      submit.innerHTML = 'Submit demo claim <span>→</span>';
    }
  }

  async function pollClaim(id, attempts) {
    if (attempts > 8) return;

    await new Promise((resolve) => setTimeout(resolve, 1000));

    try {
      const claim = await api(
        `/v1/claims/${encodeURIComponent(id)}`
      );

      const idx = claims.findIndex((c) => c.claimId === id);

      if (idx >= 0) {
        claims[idx] = claim;
      } else {
        claims.unshift(claim);
      }

      render();

      if (claim.status !== "PROCESSING") {
        showToast(
          `${id} processing complete: ${statusLabel(claim.status)}.`
        );
      } else {
        pollClaim(id, attempts + 1);
      }
    } catch (error) {
      showToast(`Status refresh failed: ${error.message}`);
    }
  }

  async function showDetails(id) {
    try {
      const c = await api(
        `/v1/claims/${encodeURIComponent(id)}`
      );

      window.alert(
        `${c.claimId}\n` +
        `Workspace: ${tenantNames[currentTenant()]}\n` +
        `Client reference: ${c.clientReference}\n` +
        `Service date: ${c.serviceDate}\n` +
        `Amount: ${formatMoney(c.amount)}\n` +
        `Status: ${statusLabel(c.status)}\n` +
        "Document filename: Document metadata only; no file stored\n\n" +
        "Local mock API only. This is not production authentication " +
        "or tenant isolation."
      );
    } catch (error) {
      showToast(error.message);
    }
  }

  // Claim submission and modal controls.
  $("newClaimTop").addEventListener("click", openModal);
  $("emptySubmit").addEventListener("click", openModal);
  $("closeModal").addEventListener("click", closeModal);
  $("cancelModal").addEventListener("click", closeModal);

  $("dismissBanner").addEventListener("click", () => {
    $("dismissBanner").closest(".demo-banner").remove();
  });

  els.form.addEventListener("submit", (event) => {
    event.preventDefault();
    createClaim(new FormData(els.form));
  });

  // Tenant switching resets pagination and reloads the first page.
  els.tenant.addEventListener("change", () => {
    document.querySelector(".breadcrumb strong").textContent = "Overview";
    loadClaims();
  });

  // Search and status filtering operate on the claims already loaded.
  els.search.addEventListener("input", render);
  els.filter.addEventListener("change", render);

  // Pagination.
  els.loadMore.addEventListener("click", loadMoreClaims);

  // Claim details.
  els.table.addEventListener("click", (event) => {
    const button = event.target.closest("[data-claim-id]");

    if (button) {
      showDetails(button.dataset.claimId);
    }
  });

  // Modal dismissal.
  els.modal.addEventListener("click", (event) => {
    if (event.target === els.modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !els.modal.hidden) {
      closeModal();
    }
  });

  // Navigation.
  document
    .querySelectorAll('.nav-link[href="#submit"]')
    .forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        openModal();
      });
    });

  document
    .querySelectorAll('.nav-link[href="#claims"]')
    .forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();

        $("claims").scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    });

  document
    .querySelectorAll('.nav-link[href="#overview"]')
    .forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();

        $("overview").scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    });

  // Connect to the local mock API.
  fetch("/v1/health")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Health check failed");
      }

      return response.json();
    })
    .then(() => {
      const banner = document.querySelector(".demo-banner span");

      if (banner) {
        banner.textContent =
          "Connected to the local mock API. Auth, tenant isolation, " +
          "and document upload remain simulated; use synthetic data only.";
      }

      loadClaims(true);
    })
    .catch(() => {
      showToast(
        "Mock API is not running. Start server.py, then reload this page."
      );
    });
})();