# AI Customer Support Copilot

An AI-powered triage dashboard for customer support teams. It takes incoming
customer complaints, analyzes them with an LLM (Claude), and surfaces a
priority-sorted queue with sentiment, category, and a suggested resolution
for each ticket — so agents can see what needs attention first and respond
faster.

![mode](https://img.shields.io/badge/AI-Claude%20%2F%20mock%20fallback-5ec9b8)
![stack](https://img.shields.io/badge/stack-Flask%20%2B%20vanilla%20JS-1b2126)

## What it does

For every complaint, the assistant determines:

- **Sentiment** — positive / neutral / negative / very negative
- **Category** — billing, technical, shipping, account, product feedback, other
- **Priority** — low / medium / high / urgent
- **Summary** — a one-line neutral restatement of the issue
- **Suggested resolution** — a concrete next step the agent can act on, not boilerplate
- **Reasoning** — why that priority was assigned

The dashboard sorts tickets by priority, lets agents filter by priority /
category / sentiment, and supports submitting new complaints live (e.g. to
simulate a fresh ticket coming in through a web form).

## Why this design

- **LLM over classic ML**: a single well-structured prompt handles sentiment,
  classification, and resolution drafting at once, generalizes to complaints
  it's never seen, and needs no training data or labeled dataset — a better
  fit for a fast-moving support inbox than a trained classifier with a
  closed label set.
- **Mock fallback mode**: if no API key is configured, the app automatically
  falls back to a deterministic keyword-based heuristic so it's fully
  demoable with zero setup. This also means the live API call path is
  exercised and tested the same way regardless of mode — useful for showing
  graceful degradation as a design pattern, not just a shortcut.
- **In-memory store**: tickets live in a Python dict for simplicity. Swapping
  in a real database (SQLite/Postgres) would only touch `app.py`.

## Project structure

```
support-copilot/
├── app.py              # Flask app & API routes
├── analyzer.py          # AI analysis: live Claude call + mock fallback + validation
├── sample_data.py        # Seed complaints so the dashboard isn't empty on first run
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html       # Dashboard markup
└── static/
    ├── style.css         # Design system (see "Design notes" below)
    └── app.js            # Fetch/render/filter logic, no framework
```

## Running it

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) enable live AI analysis
cp .env.example .env
# then edit .env and paste in your key from https://console.anthropic.com/

# 3. Run
python3 app.py
```

Open **http://localhost:5000**. The mode badge in the top bar shows whether
you're running live (calling Claude) or in mock mode (no key set, runs
entirely offline with heuristic analysis).

No API key? The app still works out of the box — every seeded ticket and
any new one you submit gets analyzed with the built-in mock heuristics.

## API

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/status` | Current AI mode (`live`/`mock`) and ticket count |
| `GET` | `/api/tickets` | List all tickets with their analysis |
| `POST` | `/api/tickets` | Submit a new complaint (`customer`, `channel`, `subject`, `message`) — runs AI analysis and returns the created ticket |
| `POST` | `/api/tickets/<id>/reanalyze` | Re-run analysis on an existing ticket |

## Design notes

The visual direction is a calm, dark "ops room" rather than a typical bright
SaaS dashboard — built for an agent scanning a queue under time pressure, not
for a marketing screenshot. A few deliberate choices:

- **Priority rail**: each ticket card has a colored left edge (not a generic
  badge) so urgency reads at a glance while scrolling, with a small pulsing
  dot reserved only for `urgent` tickets.
- **Type pairing**: Space Grotesk for headings, Source Sans 3 for body copy,
  and IBM Plex Mono specifically for machine-generated/structured fields
  (ticket IDs, timestamps, tags) — the monospace marks "the system produced
  this," contrasting with the customer's own words in the message body.
- **Priority colors** were chosen to avoid the literal red/yellow/green
  traffic-light cliché while still reading clearly as an urgency gradient.

## Extending this project

Ideas if you want to keep building:

- Swap the in-memory store for SQLite/Postgres so tickets persist across restarts
- Add authentication and per-agent ticket assignment
- Add a "mark resolved" action and resolution time tracking
- Stream the AI response token-by-token for a livelier feel on new submissions
- Add a small eval set of complaints with expected priority/category labels,
  and report accuracy of the prompt vs. the mock heuristic — good portfolio
  talking point on evaluating LLM-based classification
