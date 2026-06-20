"""
analyzer.py

Core AI logic for the Support Copilot.

Given a raw customer complaint, this module returns a structured analysis:
- sentiment (positive / neutral / negative / very_negative)
- category (billing, technical, shipping, account, product_feedback, other)
- priority (low / medium / high / urgent)
- a short reasoning/summary
- a suggested resolution the agent can use as a starting point

Two modes:
1. LIVE mode  - calls the OpenAI API with a structured prompt.
2. MOCK mode  - used automatically when no OPENAI_API_KEY is set, so the
                app is fully demoable with zero setup. Uses lightweight
                keyword heuristics to produce plausible, varied results.

The calling code (app.py) doesn't need to know which mode is active -
`analyze_complaint()` handles the fallback transparently and always
returns the same shape.
"""

import os
import json
import re
from google import genai


# Clear proxy environment variables to avoid issues with OpenAI client initialization
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

MODEL = "gemini-2.5-flash"

VALID_SENTIMENTS = {"positive", "neutral", "negative", "very_negative"}
VALID_CATEGORIES = {
    "billing",
    "technical",
    "shipping",
    "account",
    "product_feedback",
    "other",
}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


def is_live_mode() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


SYSTEM_PROMPT = """You are an AI Customer Success Copilot embedded in a customer support platform.

Your job is to help Customer Success and Support teams triage incoming customer messages so human agents can respond faster and more effectively.

For every message you are given, analyze it and return ONLY a JSON object
(no preamble, no markdown fences, no explanation outside the JSON) with exactly
these fields:

{
  "sentiment": one of "positive" | "neutral" | "negative" | "very_negative",

  "category": one of "billing" | "technical" | "shipping" | "account" | "product_feedback" | "other",

  "priority": one of "low" | "medium" | "high" | "urgent",

  "customer_impact": one of "low" | "medium" | "high",

  "escalation_required": true or false,

  "recommended_team": the most appropriate team to handle the issue
  (examples: Technical Support, Billing Team, Account Management, Product Team, Customer Success Team),

  "summary": a one-sentence neutral summary of the issue (max 20 words),

  "suggested_resolution": 2-3 sentences suggesting how the agent could resolve or respond to this, specific to the message,

  "reasoning": one short sentence explaining why you assigned this priority level
}

Guidance on priority:
- "urgent": business-critical outages, repeated billing errors, angry customers threatening to churn, \
safety issues, anything time-sensitive (e.g. an event happening soon)
- "high": significant negative experience, broken product, frustrated customer, financial impact
- "medium": real issue but not time-critical or severe, mild frustration
- "low": general questions, positive feedback, minor requests

Guidance on sentiment:
- "very_negative": customer is angry, threatening to leave, or describes a significantly damaging experience
- "negative": customer is frustrated or unhappy but measured
- "neutral": purely informational, a question with no emotional charge
- "positive": satisfied, complimentary, or enthusiastic

Return ONLY the JSON object."""


def _build_user_prompt(complaint: dict) -> str:
    return (
        f"Customer: {complaint.get('customer', 'Unknown')}\n"
        f"Channel: {complaint.get('channel', 'Unknown')}\n"
        f"Subject: {complaint.get('subject', '')}\n"
        f"Message: {complaint.get('message', '')}"
    )


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model response, tolerating stray text/fences."""
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    text = text.strip()

    # If there's leading/trailing prose, grab the outermost {...}
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from response: {text[:100]}... Error: {e}")


def _validate_and_normalize(result: dict) -> dict:
    """Ensure required fields exist and fall within allowed values; clamp/default otherwise."""
    sentiment = str(result.get("sentiment", "neutral")).lower().strip()
    category = str(result.get("category", "other")).lower().strip()
    priority = str(result.get("priority", "medium")).lower().strip()

    if sentiment not in VALID_SENTIMENTS:
        sentiment = "neutral"
    if category not in VALID_CATEGORIES:
        category = "other"
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    summary = str(result.get("summary", "")).strip() or "No summary available."
    suggested_resolution = (
        str(result.get("suggested_resolution", "")).strip()
        or "Review the message and respond directly to the customer's concern."
    )
    reasoning = str(result.get("reasoning", "")).strip() or "Default priority assigned."

    return {
        "sentiment": sentiment,
        "category": category,
        "priority": priority,
        "summary": summary,
        "suggested_resolution": suggested_resolution,
        "reasoning": reasoning,
    }


def _call_gemini(complaint: dict) -> dict:
    """
    Call Gemini API and return structured analysis.
    """
    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY")
        )

        prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + _build_user_prompt(complaint)
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        raw_text = response.text

        parsed = _extract_json(raw_text)

        return _validate_and_normalize(parsed)

    except Exception as e:
        print(f"Gemini API Error: {type(e).__name__}: {str(e)}")
        raise


# ---------------------------------------------------------------------------
# Mock mode: lightweight heuristics so the app is fully usable with no API key
# ---------------------------------------------------------------------------

_URGENT_WORDS = ["urgent", "immediately", "asap", "critical", "business-critical", "right now"]
_NEGATIVE_WORDS = [
    "angry", "upset", "frustrated", "shattered", "broken", "terrible",
    "cancel", "refund", "charged twice", "locked out", "worst", "unacceptable",
    "annoying", "keeps logging me out", "didn't help",
]
_POSITIVE_WORDS = [
    "love", "fantastic", "great", "thanks", "thank you", "awesome", "wonderful",
    "cherry on top",
]

_BILLING_WORDS = ["charge", "charged", "refund", "billing", "invoice", "payment", "subscription", "price"]
_TECHNICAL_WORDS = ["app", "login", "bug", "error", "crash", "loading", "update", "password", "locked out"]
_SHIPPING_WORDS = ["shipping", "delivery", "package", "arrived", "shattered", "order", "tracking"]
_ACCOUNT_WORDS = ["account", "address", "settings", "profile", "email address"]


def _mock_analyze(complaint: dict) -> dict:
    text = f"{complaint.get('subject', '')} {complaint.get('message', '')}".lower()

    # Sentiment heuristic
    if any(w in text for w in _URGENT_WORDS) and any(w in text for w in _NEGATIVE_WORDS):
        sentiment = "very_negative"
    elif any(w in text for w in _NEGATIVE_WORDS):
        sentiment = "negative"
    elif any(w in text for w in _POSITIVE_WORDS):
        sentiment = "positive"
    else:
        sentiment = "neutral"

    # Category heuristic (first match wins, checked in a sensible order).
    # Positive feedback is checked early so compliments that happen to mention
    # a feature (e.g. "loving the new dashboard update") aren't misclassified
    # as technical/billing issues just because of an overlapping keyword.
    if sentiment == "positive":
        category = "product_feedback"
    elif any(w in text for w in _BILLING_WORDS):
        category = "billing"
    elif any(w in text for w in _ACCOUNT_WORDS) and "address" in text:
        category = "account"
    elif any(w in text for w in _TECHNICAL_WORDS):
        category = "technical"
    elif any(w in text for w in _SHIPPING_WORDS):
        category = "shipping"
    else:
        category = "other"

    # Priority heuristic
    if any(w in text for w in _URGENT_WORDS) or sentiment == "very_negative":
        priority = "urgent"
    elif sentiment == "negative":
        priority = "high"
    elif sentiment == "positive" or category == "account":
        priority = "low"
    else:
        priority = "medium"

    summary = (complaint.get("subject") or "Customer message").strip()
    if not summary.endswith("."):
        summary += "."

    resolution_map = {
        "billing": "Verify the charge in the billing system, issue a refund or correction if confirmed, "
        "and confirm the fix with the customer in writing.",
        "technical": "Ask for device/app version details, check known issues, and escalate to engineering "
        "if this matches an active bug report.",
        "shipping": "Confirm the order details, offer a replacement or refund per policy, and apologize "
        "for the inconvenience given the circumstances.",
        "account": "Walk the customer through the relevant settings page, or update the account detail "
        "directly on their behalf if permissions allow.",
        "product_feedback": "Thank the customer for the feedback and log the suggestion for the product team.",
        "other": "Review the message and route to the appropriate team for a direct response.",
    }

    reasoning_map = {
        "urgent": "Time-sensitive or business-critical language detected, requires immediate attention.",
        "high": "Customer expresses clear frustration or significant negative impact.",
        "medium": "Standard issue without urgency signals.",
        "low": "Informational request or positive feedback, no urgency.",
    }

    return {
        "sentiment": sentiment,
        "category": category,
        "priority": priority,
        "summary": summary,
        "suggested_resolution": resolution_map[category],
        "reasoning": reasoning_map[priority],
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def analyze_complaint(complaint: dict) -> dict:
    """
    Analyze a single complaint dict (expects at least 'subject' and 'message' keys).
    Returns a dict with sentiment, category, priority, summary, suggested_resolution,
    reasoning, and a 'mode' field indicating whether 'live' or 'mock' analysis was used.
    """
    if is_live_mode():
        try:
            result = _call_gemini(complaint)
            result["mode"] = "live"
            return result
        except Exception as exc:  # noqa: BLE001 - we deliberately fall back on any failure
            result = _mock_analyze(complaint)
            result["mode"] = "mock"
            result["mode_note"] = f"Live API call failed ({exc.__class__.__name__}), used fallback analysis."
            return result

    result = _mock_analyze(complaint)
    result["mode"] = "mock"
    return result
