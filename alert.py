import requests
from config import SLACK_WEBHOOK_URL, SCORE_THRESHOLD, PHANTOM_FAILURE_THRESHOLD, COST_ALERT_USD

_LABELS = {
    "frontend_engineer":         "Frontend Engineer",
    "ml_engineer":               "ML Engineer",
    "support_agent":             "Support Agent",
    "backend_engineer":          "Backend Engineer",
    "growth_marketer":           "Growth Marketer",
    "product_marketing_manager": "PMM",
}


def _post(payload: dict):
    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10).raise_for_status()


def candidate(profile: dict):
    label = _LABELS.get(profile.get("matched_profile", ""), profile.get("matched_profile", ""))
    _post({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{profile.get('full_name', 'Unknown')}* — {label} "
                        f"({profile.get('platform', '').capitalize()}) "
                        f"• Score: *{profile.get('composite_score', 0):.1f}/10*\n"
                        f"📍 {profile.get('location', 'N/A')} | _{profile.get('headline', '')}_\n"
                        f"{profile.get('reason', '')}"
                    ),
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View profile"},
                    "url": profile.get("profile_url", ""),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Suggested outreach:*\n{profile.get('outreach_draft', '')}",
                },
            },
            {"type": "divider"},
        ]
    })


def phantom_failure(platform: str, count: int):
    _post({
        "text": (
            f":warning: *Talent Radar* — {platform.capitalize()} returned only {count} profiles "
            f"(threshold: {PHANTOM_FAILURE_THRESHOLD}). Session cookie may be stale."
        )
    })


def cost_overrun(cost_usd: float):
    _post({
        "text": (
            f":money_with_wings: *Talent Radar* — Claude spend this run: ${cost_usd:.2f} "
            f"(alert threshold: ${COST_ALERT_USD})"
        )
    })


def weekly_summary(platform_stats: dict, total_cost: float, total_alerted: int):
    lines = [":mag: *Talent Radar — weekly run complete*"]
    for platform, s in platform_stats.items():
        icon = ":x:" if s["phantom_failed"] else ":white_check_mark:"
        lines.append(
            f"{icon} {platform.capitalize()}: {s['raw_count']} scraped, "
            f"{s['scored_count']} scored, {s['alerted_count']} alerted"
        )
    lines.append(f"Total alerted: *{total_alerted}* | Claude spend: ${total_cost:.2f}")
    _post({"text": "\n".join(lines)})
