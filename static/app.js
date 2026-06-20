/* ==========================================================================
   Support Copilot — frontend logic
   Fetches tickets from the Flask API, renders the priority-sorted queue,
   handles filtering, new-ticket submission, and the detail view.
   ========================================================================== */

const state = {
  tickets: [],
  filters: {
    priority: new Set(["urgent", "high", "medium", "low"]),
    category: new Set(["billing", "technical", "shipping", "account", "product_feedback", "other"]),
    sentiment: new Set(["very_negative", "negative", "neutral", "positive"]),
  },
};

const PRIORITY_ORDER = { urgent: 0, high: 1, medium: 2, low: 3 };
const CATEGORY_LABELS = {
  billing: "Billing",
  technical: "Technical",
  shipping: "Shipping",
  account: "Account",
  product_feedback: "Feedback",
  other: "Other",
};
const SENTIMENT_LABELS = {
  very_negative: "Very negative",
  negative: "Negative",
  neutral: "Neutral",
  positive: "Positive",
};

// ---------------------------------------------------------------------------
// Data fetching
// ---------------------------------------------------------------------------

async function loadStatus() {
  const res = await fetch("/api/status");
  const data = await res.json();
  const pill = document.getElementById("modePill");
  if (data.mode === "live") {
    pill.textContent = "Live AI (Gemini)";
    pill.classList.add("live");
  } else {
    pill.textContent = "Mock mode (no API key)";
    pill.classList.add("mock");
  }
}

async function loadTickets() {
  const res = await fetch("/api/tickets");
  state.tickets = await res.json();
  renderStats();
  renderTickets();
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function renderStats() {
  const urgent = state.tickets.filter((t) => t.analysis?.priority === "urgent").length;
  const high = state.tickets.filter((t) => t.analysis?.priority === "high").length;
  document.getElementById("statUrgent").textContent = urgent;
  document.getElementById("statHigh").textContent = high;
  document.getElementById("statTotal").textContent = state.tickets.length;
}

function applyFilters(tickets) {
  return tickets.filter((t) => {
    const a = t.analysis || {};
    return (
      state.filters.priority.has(a.priority) &&
      state.filters.category.has(a.category) &&
      state.filters.sentiment.has(a.sentiment)
    );
  });
}

function sortByPriority(tickets) {
  return [...tickets].sort((a, b) => {
    const pa = PRIORITY_ORDER[a.analysis?.priority] ?? 9;
    const pb = PRIORITY_ORDER[b.analysis?.priority] ?? 9;
    if (pa !== pb) return pa - pb;
    return new Date(b.created_at) - new Date(a.created_at);
  });
}

function formatTime(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderTickets() {
  const list = document.getElementById("ticketList");
  const emptyState = document.getElementById("emptyState");
  const filtered = sortByPriority(applyFilters(state.tickets));

  list.innerHTML = "";

  if (filtered.length === 0) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  for (const ticket of filtered) {
    list.appendChild(buildTicketCard(ticket));
  }
}

function buildTicketCard(ticket) {
  const a = ticket.analysis || {};
  const card = document.createElement("div");
  card.className = "ticket-card";
  card.addEventListener("click", () => openDetail(ticket));

  const rail = document.createElement("div");
  rail.className = `priority-rail ${a.priority || "medium"}`;

  const main = document.createElement("div");
  main.className = "ticket-main";

  const topRow = document.createElement("div");
  topRow.className = "ticket-top-row";
  topRow.innerHTML = `
    <span class="ticket-id">${escapeHtml(ticket.id)}</span>
    <span class="ticket-customer">${escapeHtml(ticket.customer)}</span>
    <span class="ticket-channel">${escapeHtml(ticket.channel)}</span>
    ${a.priority === "urgent" ? '<span class="pulse-dot"></span>' : ""}
  `;

  const subject = document.createElement("p");
  subject.className = "ticket-subject";
  subject.textContent = ticket.subject;

  const summary = document.createElement("p");
  summary.className = "ticket-summary";
  summary.textContent = a.summary || "";

  main.appendChild(topRow);
  main.appendChild(subject);
  main.appendChild(summary);

  const tags = document.createElement("div");
  tags.className = "ticket-tags";
  tags.innerHTML = `
    <span class="tag tag-priority ${a.priority || "medium"}">${a.priority || "—"}</span>
    <span class="tag tag-category">${CATEGORY_LABELS[a.category] || a.category || "—"}</span>
    <span class="ticket-time">${formatTime(ticket.created_at)}</span>
  `;

  card.appendChild(rail);
  card.appendChild(main);
  card.appendChild(tags);
  return card;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Detail modal
// ---------------------------------------------------------------------------

function openDetail(ticket) {
  const a = ticket.analysis || {};
  const modal = document.getElementById("detailModal");

  modal.innerHTML = `
    <div class="modal-header">
      <h3>${escapeHtml(ticket.subject)}</h3>
      <button class="modal-close" id="detailClose">&times;</button>
    </div>
    <div class="detail-section">
      <div class="detail-meta-row">
        <span><strong>${escapeHtml(ticket.customer)}</strong></span>
        <span>${escapeHtml(ticket.channel)}</span>
        <span>${escapeHtml(ticket.id)}</span>
        <span>${formatTime(ticket.created_at)}</span>
      </div>
      <div class="detail-tags" style="margin-top:12px;">
        <span class="tag tag-priority ${a.priority}">${a.priority}</span>
        <span class="tag tag-category">${CATEGORY_LABELS[a.category] || a.category}</span>
        <span class="tag tag-category">${SENTIMENT_LABELS[a.sentiment] || a.sentiment}</span>
      </div>
    </div>
    <div class="detail-section">
      <p class="detail-label">Customer message</p>
      <p class="detail-message">${escapeHtml(ticket.message)}</p>
    </div>
    <div class="detail-section">
      <p class="detail-label">AI suggested resolution</p>
      <div class="resolution-box">${escapeHtml(a.suggested_resolution)}</div>
      <p class="reasoning-note">Why this priority: ${escapeHtml(a.reasoning || "")}</p>
      ${a.mode === "mock" ? '<p class="mode-note">⚠ Generated in mock mode (no live API key configured)</p>' : ""}
      ${a.mode_note ? `<p class="mode-note">⚠ ${escapeHtml(a.mode_note)}</p>` : ""}
    </div>
  `;

  document.getElementById("detailClose").addEventListener("click", closeDetail);
  document.getElementById("detailBackdrop").hidden = false;
}

function closeDetail() {
  document.getElementById("detailBackdrop").hidden = true;
}

// ---------------------------------------------------------------------------
// New ticket form
// ---------------------------------------------------------------------------

function openNewTicketModal() {
  document.getElementById("ticketForm").reset();
  document.getElementById("modalBackdrop").hidden = false;
}

function closeNewTicketModal() {
  document.getElementById("modalBackdrop").hidden = true;
}

async function handleSubmit(event) {
  event.preventDefault();
  const submitBtn = document.getElementById("submitBtn");
  const originalText = submitBtn.textContent;
  submitBtn.textContent = "Analyzing…";
  submitBtn.disabled = true;

  const payload = {
    customer: document.getElementById("customer").value,
    channel: document.getElementById("channel").value,
    subject: document.getElementById("subject").value,
    message: document.getElementById("message").value,
  };

  try {
    const res = await fetch("/api/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.error || "Something went wrong submitting the ticket.");
      return;
    }
    closeNewTicketModal();
    await loadTickets();
  } catch (err) {
    alert("Network error — could not reach the server.");
  } finally {
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
  }
}

// ---------------------------------------------------------------------------
// Filter wiring
// ---------------------------------------------------------------------------

function wireFilterGroup(selector, filterSet) {
  document.querySelectorAll(selector).forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        filterSet.add(checkbox.value);
      } else {
        filterSet.delete(checkbox.value);
      }
      renderTickets();
    });
  });
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  loadStatus();
  loadTickets();

  document.getElementById("newTicketBtn").addEventListener("click", openNewTicketModal);
  document.getElementById("modalClose").addEventListener("click", closeNewTicketModal);
  document.getElementById("cancelBtn").addEventListener("click", closeNewTicketModal);
  document.getElementById("ticketForm").addEventListener("submit", handleSubmit);

  document.getElementById("modalBackdrop").addEventListener("click", (e) => {
    if (e.target.id === "modalBackdrop") closeNewTicketModal();
  });
  document.getElementById("detailBackdrop").addEventListener("click", (e) => {
    if (e.target.id === "detailBackdrop") closeDetail();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeNewTicketModal();
      closeDetail();
    }
  });

  wireFilterGroup(".f-priority", state.filters.priority);
  wireFilterGroup(".f-category", state.filters.category);
  wireFilterGroup(".f-sentiment", state.filters.sentiment);
});
