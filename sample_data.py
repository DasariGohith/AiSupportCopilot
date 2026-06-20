"""
Seed data: sample customer complaints used to populate the dashboard on first run
and to power mock mode when no API key is configured.
"""

SAMPLE_COMPLAINTS = [
    {
        "id": "t-1001",
        "customer": "Priya Nair",
        "channel": "Email",
        "subject": "Charged twice for the same order",
        "message": (
            "I was charged twice for order #48213 placed last Tuesday. "
            "I've checked my bank statement and there are two identical charges of $89.99. "
            "I need this refunded immediately, this is the second time this has happened "
            "and I'm honestly considering cancelling my subscription."
        ),
        "created_at": "2026-06-18T09:14:00",

        "analysis": {
    "sentiment": "negative",
    "category": "billing",
    "priority": "high",
    "summary": "Customer reports duplicate charges for a single order.",
    "suggested_resolution": "Verify the payment records, confirm the duplicate transaction, and process a refund. Apologize for the inconvenience and reassure the customer that the issue is being investigated.",
    "reasoning": "Financial impact and repeated occurrence increase urgency."
}
    },
    {
        "id": "t-1002",
        "customer": "Daniel Osei",
        "channel": "Chat",
        "subject": "How do I update my shipping address?",
        "message": (
            "Hey, quick question - I moved last month and want to update my default "
            "shipping address for future orders. Couldn't find it in account settings, "
            "is it somewhere else?"
        ),
        "created_at": "2026-06-18T11:02:00",

        "analysis": {
    "sentiment": "neutral",
    "category": "account",
    "priority": "low",
    "summary": "Customer needs help updating their shipping address.",
    "suggested_resolution": "Guide the customer to the address management section or provide step-by-step instructions. Confirm that future orders will use the updated address.",
    "reasoning": "Informational request with no immediate business impact."
}
    },
    {
        "id": "t-1003",
        "customer": "Maria Lopez",
        "channel": "Phone (transcribed)",
        "subject": "Product arrived completely shattered",
        "message": (
            "I ordered the ceramic vase set as a wedding gift and it arrived in pieces. "
            "Like, completely shattered, packaging was barely there. The wedding is this "
            "weekend and now I have nothing to give. I'm really upset about this, it was "
            "supposed to be special."
        ),
        "created_at": "2026-06-19T08:40:00",

        "analysis": {
    "sentiment": "very_negative",
    "category": "shipping",
    "priority": "high",
    "summary": "Customer received a damaged product intended as a gift.",
    "suggested_resolution": "Arrange an expedited replacement or refund immediately. Apologize for the damaged shipment and coordinate with logistics to investigate packaging issues.",
    "reasoning": "Customer is highly dissatisfied and faces a time-sensitive event."
}
    },
    {
        "id": "t-1004",
        "customer": "Tom Becker",
        "channel": "Email",
        "subject": "Login issues on mobile app",
        "message": (
            "The app keeps logging me out every few minutes on my Android phone. "
            "Happens consistently since the last update. Reinstalled twice, didn't help. "
            "Kind of annoying but I can still use the desktop site for now."
        ),
        "created_at": "2026-06-19T14:23:00",

        "analysis": {
    "sentiment": "negative",
    "category": "technical",
    "priority": "medium",
    "summary": "Customer experiences repeated logout issues after a mobile app update.",
    "suggested_resolution": "Collect device and app version details, investigate the latest release, and provide troubleshooting steps. Escalate to engineering if the issue is reproducible.",
    "reasoning": "Service remains usable through desktop, reducing urgency."
}
    },
    {
        "id": "t-1005",
        "customer": "Aisha Rahman",
        "channel": "Chat",
        "subject": "Loving the new dashboard update!",
        "message": (
            "Just wanted to say the new analytics dashboard you rolled out is fantastic, "
            "so much easier to find what I need now. One small thing - could you add a way "
            "to export to CSV? Would be the cherry on top."
        ),
        "created_at": "2026-06-19T16:55:00",

        "analysis": {
    "sentiment": "positive",
    "category": "product_feedback",
    "priority": "low",
    "summary": "Customer praises the dashboard and suggests CSV export functionality.",
    "suggested_resolution": "Thank the customer for the feedback and forward the feature request to the product team for consideration.",
    "reasoning": "Positive feedback with a non-urgent enhancement request."
}
    },
    {
        "id": "t-1006",
        "customer": "James Whitfield",
        "channel": "Email",
        "subject": "URGENT: Account locked, can't access payroll data",
        "message": (
            "Our entire finance team is locked out of the account right before payroll "
            "is due to run. We've tried password resets twice and still nothing. This is "
            "a business-critical outage for us, we need someone to call us back immediately. "
            "We are a paying enterprise customer on the annual plan."
        ),
        "created_at": "2026-06-20T07:05:00",

        "analysis": {
    "sentiment": "very_negative",
    "category": "account",
    "priority": "urgent",
    "summary": "Enterprise customer is locked out before payroll processing.",
    "suggested_resolution": "Escalate immediately to the account recovery team, verify ownership, and restore access as a business-critical incident. Provide continuous updates until resolution.",
    "reasoning": "Business operations are blocked for an enterprise customer."
}
    },
    {
        "id": "t-1007",
        "customer": "Sofia Conti",
        "channel": "Chat",
        "subject": "Question about return window",
        "message": (
            "Hi, what's the return window for items bought during the spring sale? "
            "Just want to check before I open the box."
        ),
        "created_at": "2026-06-20T09:30:00",

        "analysis": {
    "sentiment": "neutral",
    "category": "other",
    "priority": "low",
    "summary": "Customer is asking about the return policy for sale items.",
    "suggested_resolution": "Provide the applicable return policy and clarify any exceptions related to promotional purchases.",
    "reasoning": "General inquiry with no service disruption."
}
    },
]
