"""
app.py

Flask application for the AI Customer Support Copilot.

Routes:
  GET  /                  -> dashboard UI
  GET  /api/tickets       -> list all tickets (with analysis, if available)
  POST /api/tickets       -> submit a new complaint, runs AI analysis, returns the ticket
  POST /api/tickets/<id>/reanalyze -> re-run analysis on an existing ticket
  GET  /api/status        -> whether the app is running in live or mock AI mode
"""

import os
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from analyzer import analyze_complaint, is_live_mode
from sample_data import SAMPLE_COMPLAINTS

load_dotenv()

app = Flask(__name__)

# In-memory ticket store (fine for a portfolio demo; swap for a DB in production)
TICKETS = {}


def _seed_tickets():
    for complaint in SAMPLE_COMPLAINTS:
        TICKETS[complaint["id"]] = complaint


_seed_tickets()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify(
        {
            "mode": "live" if is_live_mode() else "mock",
            "ticket_count": len(TICKETS),
        }
    )


@app.route("/api/tickets", methods=["GET"])
def list_tickets():
    tickets = list(TICKETS.values())
    tickets.sort(key=lambda t: t["created_at"], reverse=True)
    return jsonify(tickets)


@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(force=True, silent=True) or {}

    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "A 'message' field is required."}), 400

    complaint = {
        "id": f"t-{uuid.uuid4().hex[:8]}",
        "customer": (data.get("customer") or "Anonymous").strip(),
        "channel": (data.get("channel") or "Web Form").strip(),
        "subject": (data.get("subject") or "").strip() or message[:60],
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    complaint["analysis"] = analyze_complaint(complaint)
    TICKETS[complaint["id"]] = complaint

    return jsonify(complaint), 201


@app.route("/api/tickets/<ticket_id>/reanalyze", methods=["POST"])
def reanalyze_ticket(ticket_id):
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    ticket["analysis"] = analyze_complaint(ticket)
    return jsonify(ticket)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n  AI Support Copilot running at http://localhost:{port}")
    print(f"  AI mode: {'LIVE (Gemini API)' if is_live_mode() else 'MOCK (no API key set)'}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
