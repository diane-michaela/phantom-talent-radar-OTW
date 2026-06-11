import json
import anthropic
from config import ANTHROPIC_API_KEY, PROFILES, GEOGRAPHIES, HAIKU_INPUT_COST, HAIKU_OUTPUT_COST

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
_MODEL  = "claude-haiku-4-5-20251001"

_SYSTEM = (
    f"You are a recruiter assistant. Roles we hire for: {', '.join(PROFILES)}. "
    f"Target geographies: {', '.join(GEOGRAPHIES)}. "
    "Respond with valid JSON only, no extra text."
)

_PROMPT = """Score this candidate on 5 dimensions (0–10 each):
1. location — are they in France, Spain, or Portugal?
2. availability — do they actively signal they're looking right now?
3. skills — do their skills match one of the 6 target roles?
4. authenticity — is this a real, detailed profile (not a bot)?
5. language — is their content in French, Spanish, Portuguese, or English?

Name: {full_name}
Platform: {platform}
Location: {location}
Headline: {headline}
Bio: {bio_text}

Return exactly this JSON:
{{
  "matched_profile": "<frontend_engineer|ml_engineer|support_agent|backend_engineer|growth_marketer|product_marketing_manager|none>",
  "score_location": <0-10>,
  "score_availability": <0-10>,
  "score_skills": <0-10>,
  "score_authenticity": <0-10>,
  "score_language": <0-10>,
  "composite_score": <average of the 5 scores, 1 decimal>,
  "reason": "<2 sentences explaining the score>",
  "outreach_draft": "<short personalised outreach in the candidate's language — empty string if composite_score < 7>"
}}"""


def _call(profile: dict) -> dict | None:
    prompt = _PROMPT.format(**profile)
    for attempt in range(2):
        try:
            msg = _client.messages.create(
                model=_MODEL,
                max_tokens=512,
                temperature=0.2,
                system=_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            result = json.loads(msg.content[0].text.strip())
            result["_in"]  = msg.usage.input_tokens
            result["_out"] = msg.usage.output_tokens
            return result
        except json.JSONDecodeError:
            if attempt == 0:
                print(f"[score] malformed JSON for {profile['profile_url']}, retrying...")
            else:
                print(f"[score] skip {profile['profile_url']}: could not parse Claude response")
        except Exception as e:
            print(f"[score] error on {profile['profile_url']}: {e}")
            return None
    return None


def score_all(profiles: list) -> tuple:
    scored = []
    total_cost = 0.0
    for profile in profiles:
        result = _call(profile)
        if result is None:
            continue
        cost = result.pop("_in") * HAIKU_INPUT_COST + result.pop("_out") * HAIKU_OUTPUT_COST
        total_cost += cost
        profile.update(result)
        scored.append(profile)
    return scored, total_cost
