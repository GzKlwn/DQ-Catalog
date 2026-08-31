import { ICONS } from "./icons.js";

// ---------------------------------------------------------------------------
// icon injection
// ---------------------------------------------------------------------------
function renderIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    const name = el.getAttribute("data-icon");
    if (ICONS[name] && !el.dataset.rendered) {
      el.innerHTML = ICONS[name];
      el.dataset.rendered = "1";
    }
  });
}

// ---------------------------------------------------------------------------
// tabs
// ---------------------------------------------------------------------------
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => switchView(tab.dataset.view));
});

function switchView(view) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === view));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${view}`));
}

// ---------------------------------------------------------------------------
// catalog state
// ---------------------------------------------------------------------------
const FACETS = [
  { key: "object", label: "Object", isList: false },
  { key: "domain", label: "Domain", isList: false },
  { key: "tables", label: "Table", isList: true },
  { key: "fields", label: "Field", isList: true },
  { key: "industries", label: "Industry", isList: true },
];

let allRules = [];
let searchQuery = "";
const activeFilters = {}; // key -> Set(values); "criticality" can appear too even without a chip group

function uniqueValues(key, isList) {
  const set = new Set();
  for (const r of allRules) {
    const v = r[key];
    if (isList) (v || []).forEach((x) => set.add(x));
    else if (v) set.add(v);
  }
  return [...set].sort();
}

function ruleMatchesFacet(rule, key, isList, values) {
  if (!values || values.size === 0) return true;
  if (isList) return (rule[key] || []).some((v) => values.has(v));
  return values.has(rule[key]);
}

function filteredRules() {
  const q = searchQuery.trim().toLowerCase();
  return allRules.filter((r) => {
    for (const f of FACETS) {
      if (!ruleMatchesFacet(r, f.key, f.isList, activeFilters[f.key])) return false;
    }
    if (activeFilters.criticality && activeFilters.criticality.size && !activeFilters.criticality.has(r.criticality)) {
      return false;
    }
    if (q && !(`${r.name} ${r.description || ""}`.toLowerCase().includes(q))) return false;
    return true;
  });
}

function toggleFilter(key, value) {
  if (!activeFilters[key]) activeFilters[key] = new Set();
  if (activeFilters[key].has(value)) activeFilters[key].delete(value);
  else activeFilters[key].add(value);
  renderFacets();
  renderActiveFilters();
  renderGrid();
}

function setFilter(key, value) {
  // Jumping in from a Summary bar should show a fresh, single-facet view —
  // not compound with whatever was still active in the Catalog tab.
  for (const k of Object.keys(activeFilters)) delete activeFilters[k];
  activeFilters[key] = new Set([value]);
  renderFacets();
  renderActiveFilters();
  renderGrid();
}

function clearAllFilters() {
  for (const k of Object.keys(activeFilters)) delete activeFilters[k];
  renderFacets();
  renderActiveFilters();
  renderGrid();
}

// ---------------------------------------------------------------------------
// rendering: filter bar
// ---------------------------------------------------------------------------
function renderFacets() {
  const root = document.getElementById("facet-groups");
  root.innerHTML = "";
  for (const f of FACETS) {
    const values = uniqueValues(f.key, f.isList);
    if (values.length === 0) continue;
    const group = document.createElement("div");
    group.className = "facet-group";
    group.innerHTML = `<div class="facet-label"><span class="icon-slot" data-icon="Filter"></span>${f.label}</div>`;
    const valuesEl = document.createElement("div");
    valuesEl.className = "facet-values";
    for (const v of values) {
      const active = activeFilters[f.key] && activeFilters[f.key].has(v);
      const chip = document.createElement("button");
      chip.className = "facet-chip" + (active ? " active" : "");
      chip.textContent = v;
      chip.addEventListener("click", () => toggleFilter(f.key, v));
      valuesEl.appendChild(chip);
    }
    group.appendChild(valuesEl);
    root.appendChild(group);
  }
  renderIcons(root);
}

function renderActiveFilters() {
  const root = document.getElementById("active-filters");
  root.innerHTML = "";
  const entries = [];
  for (const [key, set] of Object.entries(activeFilters)) {
    for (const v of set) entries.push([key, v]);
  }
  if (entries.length === 0) return;
  for (const [key, v] of entries) {
    const pill = document.createElement("span");
    pill.className = "active-pill";
    pill.innerHTML = `${key}: <b>${v}</b> <button aria-label="remove">×</button>`;
    pill.querySelector("button").addEventListener("click", () => toggleFilter(key, v));
    root.appendChild(pill);
  }
  const clearBtn = document.createElement("button");
  clearBtn.className = "clear-all";
  clearBtn.textContent = "Clear all";
  clearBtn.addEventListener("click", clearAllFilters);
  root.appendChild(clearBtn);
}

// ---------------------------------------------------------------------------
// rendering: rule grid + multi-select
// ---------------------------------------------------------------------------
const selectedRules = new Set();

function toggleSelect(name) {
  if (selectedRules.has(name)) selectedRules.delete(name);
  else selectedRules.add(name);
  renderGrid();
}

function selectAllFiltered() {
  filteredRules().forEach((r) => selectedRules.add(r.name));
  renderGrid();
}

function clearSelection() {
  selectedRules.clear();
  renderGrid();
}

function renderSelectionBar() {
  const bar = document.getElementById("selection-bar");
  const visibleCount = filteredRules().length;
  if (selectedRules.size === 0) {
    bar.classList.remove("active");
    bar.innerHTML = "";
    return;
  }
  bar.classList.add("active");
  bar.innerHTML = `
    <span class="sel-count">${selectedRules.size} selected</span>
    <button class="btn-link" id="sel-all-filtered">Select all filtered (${visibleCount})</button>
    <button class="btn-link" id="sel-clear">Clear selection</button>
    <button class="btn btn-primary" id="sel-download">
      <span class="icon-slot" data-icon="Download"></span>Download ${selectedRules.size} rule${selectedRules.size === 1 ? "" : "s"}
    </button>
  `;
  renderIcons(bar);
  document.getElementById("sel-all-filtered").addEventListener("click", selectAllFiltered);
  document.getElementById("sel-clear").addEventListener("click", clearSelection);
  document.getElementById("sel-download").addEventListener("click", openBulkDownloadPrompt);
}

function renderGrid() {
  const root = document.getElementById("rule-grid");
  const rules = filteredRules();
  root.innerHTML = "";
  if (rules.length === 0) {
    root.innerHTML = `<div class="empty-state">No rules match the current filters.</div>`;
  } else {
    for (const r of rules) {
      const selected = selectedRules.has(r.name);
      const card = document.createElement("article");
      card.className = `card accent rule-card crit-${r.criticality || ""}${selected ? " selected" : ""}`;
      const chips = [...(r.tables || []).slice(0, 3), ...(r.industries || [])]
        .map((c) => `<span class="chip">${c}</span>`)
        .join("");
      card.innerHTML = `
        <input type="checkbox" class="rc-select" ${selected ? "checked" : ""} title="Select for bulk download">
        <div class="rc-name">${r.name}</div>
        <div class="rc-object"><b>${r.object || "—"}</b> · ${r.domain || "—"} · ${r.criticality || "—"}</div>
        <div class="rc-chips">${chips}</div>
      `;
      card.querySelector(".rc-select").addEventListener("click", (e) => {
        e.stopPropagation();
        toggleSelect(r.name);
      });
      card.addEventListener("click", () => openDetail(r.name));
      root.appendChild(card);
    }
  }
  renderSelectionBar();
}

// ---------------------------------------------------------------------------
// detail modal
// ---------------------------------------------------------------------------
async function openDetail(name) {
  const detail = await fetch(`/api/rules/${encodeURIComponent(name)}`).then((r) => r.json());
  const modalBody = document.getElementById("modal-body");
  const chips = [...(detail.tables || []), ...(detail.industries || [])]
    .map((c) => `<span class="chip">${c}</span>`)
    .join("");
  const fieldTags = (detail.fields || []).map((f) => `<span class="chip">${f}</span>`).join("");
  const checks = detail.checks || {};
  modalBody.innerHTML = `
    <h2>${detail.title || detail.name}</h2>
    <div class="modal-meta">${chips}</div>
    <div class="modal-section">
      <h3>Description</h3>
      <p>${detail.description || "—"}</p>
    </div>
    <div class="modal-section">
      <h3>DQ Checks</h3>
      <div class="fcr-row"><b>Fetch</b><span>${checks.fetch || "—"}</span></div>
      <div class="fcr-row"><b>Check</b><span>${checks.check || "—"}</span></div>
      <div class="fcr-row"><b>Return</b><span>${checks.return || "—"}</span></div>
    </div>
    <div class="modal-section">
      <h3>Fields</h3>
      <div class="field-tag-list">${fieldTags}</div>
    </div>
    <div class="modal-section">
      <h3>OptSel SQL</h3>
      <div class="sql-block">${escapeHtml(detail.optselSql || "—")}</div>
    </div>
    <div class="modal-section">
      <h3>Download for a source system</h3>
      <p>Replaces every <code>{SOURCE_SYSTEM}</code> / <code>{SOURCE_SYSTEM_ID}</code> placeholder with the value below.</p>
      <div class="download-row">
        <input id="download-system-id" type="text" placeholder="e.g. Z02">
        <button class="btn btn-primary" id="download-btn"><span class="icon-slot" data-icon="Download"></span>Download</button>
      </div>
    </div>
  `;
  renderIcons(modalBody);
  document.getElementById("download-btn").addEventListener("click", () => {
    const systemId = document.getElementById("download-system-id").value.trim();
    if (!systemId) return;
    const a = document.createElement("a");
    a.href = `/api/rules/${encodeURIComponent(detail.name)}/download?system_id=${encodeURIComponent(systemId)}`;
    a.click();
  });
  document.getElementById("modal-overlay").classList.add("open");
}

document.getElementById("modal-close").addEventListener("click", () => {
  document.getElementById("modal-overlay").classList.remove("open");
});
document.getElementById("modal-overlay").addEventListener("click", (e) => {
  if (e.target.id === "modal-overlay") e.currentTarget.classList.remove("open");
});

function escapeHtml(s) {
  return s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

// ---------------------------------------------------------------------------
// bulk download (multiple rules -> one .zip of adapted markdowns)
// ---------------------------------------------------------------------------
function openBulkDownloadPrompt() {
  const names = [...selectedRules];
  const modalBody = document.getElementById("modal-body");
  modalBody.innerHTML = `
    <div class="bulk-download-prompt">
      <h2>Download ${names.length} rule${names.length === 1 ? "" : "s"}</h2>
      <p>Each rule is written to its own <code>.md</code> file inside one <code>.zip</code>, with every
      <code>{SOURCE_SYSTEM}</code> / <code>{SOURCE_SYSTEM_ID}</code> placeholder replaced by the value below.</p>
      <div class="rule-name-list">${names.map((n) => `<span class="chip">${n}</span>`).join("")}</div>
      <div class="download-row">
        <input id="bulk-system-id" type="text" placeholder="e.g. Z02">
        <button class="btn btn-primary" id="bulk-download-btn"><span class="icon-slot" data-icon="Download"></span>Download .zip</button>
      </div>
      <div id="bulk-download-status" class="rv-note"></div>
    </div>
  `;
  renderIcons(modalBody);
  document.getElementById("bulk-download-btn").addEventListener("click", () => downloadZip(names));
  document.getElementById("modal-overlay").classList.add("open");
}

async function downloadZip(names) {
  const systemId = document.getElementById("bulk-system-id").value.trim();
  const status = document.getElementById("bulk-download-status");
  if (!systemId) {
    status.textContent = "Enter a Source System ID first.";
    return;
  }
  status.textContent = "Building zip…";
  try {
    const res = await fetch("/api/rules/download-zip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ names, system_id: systemId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      status.textContent = err.error || `Download failed (${res.status}).`;
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dq-catalog-rules_${systemId}.zip`;
    a.click();
    URL.revokeObjectURL(url);
    status.textContent = "Downloaded.";
  } catch (e) {
    status.textContent = String(e);
  }
}

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------
document.getElementById("search-input").addEventListener("input", (e) => {
  searchQuery = e.target.value;
  renderGrid();
});

// ---------------------------------------------------------------------------
// summary
// ---------------------------------------------------------------------------
const DIST_TO_FILTER = {
  "dist-object": "object",
  "dist-table": "tables",
  "dist-domain": "domain",
  "dist-criticality": "criticality",
};

async function loadSummary() {
  const stats = await fetch("/api/stats").then((r) => r.json());
  document.getElementById("stat-total").textContent = stats.total;
  document.getElementById("stat-objects").textContent = stats.totalObjects;
  document.getElementById("stat-tables").textContent = stats.totalTables;
  renderBarList("dist-object", stats.byObject);
  renderBarList("dist-table", stats.byTable.slice(0, 12));
  renderBarList("dist-domain", stats.byDomain);
  renderBarList("dist-criticality", stats.byCriticality);
}

function renderBarList(containerId, entries) {
  const root = document.getElementById(containerId);
  root.innerHTML = "";
  if (!entries.length) {
    root.innerHTML = `<div class="empty-state">No data yet.</div>`;
    return;
  }
  const max = Math.max(...entries.map(([, c]) => c));
  const filterKey = DIST_TO_FILTER[containerId];
  for (const [label, count] of entries) {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label" title="${label}">${label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(count / max) * 100}%"></div></div>
      <div class="bar-count">${count}</div>
    `;
    row.addEventListener("click", () => {
      setFilter(filterKey, label);
      switchView("catalog");
      document.querySelector('.tab[data-view="catalog"]').classList.add("active");
      document.querySelector('.tab[data-view="summary"]').classList.remove("active");
    });
    root.appendChild(row);
  }
}

// ---------------------------------------------------------------------------
// upload
// ---------------------------------------------------------------------------
let pendingUploadFiles = [];

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("drag-over");
  handleFiles(e.dataTransfer.files);
});
fileInput.addEventListener("change", () => handleFiles(fileInput.files));

async function handleFiles(fileList) {
  const files = [...fileList].filter((f) => f.name.endsWith(".md"));
  if (!files.length) return;
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f, f.name));
  const res = await fetch("/api/upload/parse", { method: "POST", body: formData });
  const data = await res.json();
  if (data.error) {
    showUploadResult(false, data.error);
    return;
  }
  pendingUploadFiles = data.rules;
  renderReviewList();
}

function renderReviewList() {
  const root = document.getElementById("review-list");
  root.innerHTML = "";
  for (const [i, r] of pendingUploadFiles.entries()) {
    if (r.error) {
      root.innerHTML += `<div class="card review-card"><p>${r.filename}: ${r.error}</p></div>`;
      continue;
    }
    const m = r.metadata;
    const card = document.createElement("div");
    card.className = "card review-card";
    card.innerHTML = `
      <div class="rv-title">
        <span class="name">${r.name}</span>
        ${r.existsAlready ? '<span class="chip">will update existing rule</span>' : '<span class="chip">new rule</span>'}
      </div>
      <div class="rv-grid">
        <div class="rv-field"><label>Object</label><input data-f="object" value="${m.object || ""}" placeholder="e.g. Customer"></div>
        <div class="rv-field"><label>Domain</label><input data-f="domain" value="${m.domain || ""}"></div>
        <div class="rv-field"><label>Data type</label>
          <select data-f="dataType">
            <option ${m.dataType === "Master Data" ? "selected" : ""}>Master Data</option>
            <option ${m.dataType === "Transactional Data" ? "selected" : ""}>Transactional Data</option>
          </select>
        </div>
        <div class="rv-field"><label>Criticality</label>
          <select data-f="criticality">
            <option ${m.criticality === "High" ? "selected" : ""}>High</option>
            <option ${m.criticality === "Medium" ? "selected" : ""}>Medium</option>
            <option ${m.criticality === "Low" ? "selected" : ""}>Low</option>
          </select>
        </div>
        <div class="rv-field full"><label>Industries (comma-separated)</label><input data-f="industries" value="${(m.industries || []).join(", ")}" placeholder="e.g. Finance, Manufacturing"></div>
        <div class="rv-field full"><label>Tables (comma-separated)</label><input data-f="tables" value="${(m.tables || []).join(", ")}"></div>
        <div class="rv-field full"><label>Fields (comma-separated)</label><input data-f="fields" value="${(m.fields || []).join(", ")}"></div>
        <div class="rv-field full"><label>Description</label><textarea data-f="description">${m.description || ""}</textarea></div>
      </div>
      <div class="rv-note">Parsed automatically from the markdown's Rule Header / Output Fields tables — review before pushing.</div>
    `;
    card.querySelectorAll("[data-f]").forEach((el) => {
      el.addEventListener("input", () => {
        const field = el.dataset.f;
        if (field === "industries" || field === "tables" || field === "fields") {
          m[field] = el.value.split(",").map((s) => s.trim()).filter(Boolean);
        } else {
          m[field] = el.value;
        }
      });
    });
    root.appendChild(card);
  }
  document.getElementById("upload-actions").style.display = pendingUploadFiles.some((r) => !r.error) ? "flex" : "none";
  document.getElementById("upload-result").innerHTML = "";
}

document.getElementById("btn-cancel-upload").addEventListener("click", () => {
  pendingUploadFiles = [];
  document.getElementById("review-list").innerHTML = "";
  document.getElementById("upload-actions").style.display = "none";
  fileInput.value = "";
});

document.getElementById("btn-push").addEventListener("click", async () => {
  const btn = document.getElementById("btn-push");
  btn.disabled = true;
  const rulesToPush = pendingUploadFiles.filter((r) => !r.error).map((r) => ({
    name: r.name,
    markdown: r.markdown,
    metadata: r.metadata,
  }));
  try {
    const res = await fetch("/api/upload/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rules: rulesToPush }),
    });
    const data = await res.json();
    if (data.prUrl) {
      showUploadResult(true, `Pushed ${data.names.join(", ")} — <a href="${data.prUrl}" target="_blank" rel="noopener">open the PR</a> and review the diff on GitHub before merging.`);
      pendingUploadFiles = [];
      document.getElementById("review-list").innerHTML = "";
      document.getElementById("upload-actions").style.display = "none";
      fileInput.value = "";
      loadRules(); // refresh catalog/summary with the (soon-to-be-merged) view unaffected until merge, but keeps local state fresh
    } else {
      showUploadResult(false, `Pushed branch <code>${data.branch || "?"}</code> but ${data.error || "PR creation failed"}.`);
    }
  } catch (e) {
    showUploadResult(false, String(e));
  } finally {
    btn.disabled = false;
  }
});

function showUploadResult(ok, html) {
  document.getElementById("upload-result").innerHTML = `<div class="result-banner ${ok ? "ok" : "err"}">${html}</div>`;
}

// ---------------------------------------------------------------------------
// boot
// ---------------------------------------------------------------------------
async function loadRules() {
  allRules = await fetch("/api/rules").then((r) => r.json());
  renderFacets();
  renderActiveFilters();
  renderGrid();
}

renderIcons();
loadRules();
loadSummary();
