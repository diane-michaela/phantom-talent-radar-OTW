import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

PB_API_KEY = os.environ["PB_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

PHANTOM_IDS = {
    "linkedin": os.environ["PB_PHANTOM_LINKEDIN"],
    "twitter": os.environ["PB_PHANTOM_TWITTER"],
    "github":   os.environ["PB_PHANTOM_GITHUB"],
    "reddit":   os.environ["PB_PHANTOM_REDDIT"],
}

PROFILES = [
    "frontend_engineer",
    "ml_engineer",
    "support_agent",
    "backend_engineer",
    "growth_marketer",
    "product_marketing_manager",
]

GEOGRAPHIES = ["France", "Spain", "Portugal"]

SCORE_THRESHOLD = 7.0
MAX_PROFILES_PER_PHANTOM = 75
PHANTOM_FAILURE_THRESHOLD = 5   # < 5 raw profiles triggers a Slack warning
COST_ALERT_USD = 3.0            # flag if Claude spend exceeds this per run

DB_PATH = os.path.join(os.path.dirname(__file__), "talent_radar.db")

# claude-haiku-4-5 pricing (USD per token)
HAIKU_INPUT_COST  = 0.80  / 1_000_000
HAIKU_OUTPUT_COST = 4.00  / 1_000_000
