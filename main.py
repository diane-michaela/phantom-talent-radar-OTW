import uuid
from datetime import datetime, timezone

import alert
from config import SCORE_THRESHOLD, PHANTOM_FAILURE_THRESHOLD, COST_ALERT_USD
from db import init_db, upsert_profile
from normalise import normalise_all
from run import run_all
from score import score_all


def main():
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_id   = str(uuid.uuid4())[:8]
    print(f"[main] Talent Radar run {run_id} — {run_date}")

    init_db()

    # 1. Launch and collect phantom output
    raw_results = run_all()

    # 2. Keyword pre-filter + normalise to common schema
    profiles = normalise_all(raw_results)
    print(f"[main] {len(profiles)} profiles after normalisation")

    # 3. Score with Claude
    scored, total_cost = score_all(profiles)
    print(f"[main] {len(scored)} profiles scored — est. cost ${total_cost:.3f}")

    if total_cost > COST_ALERT_USD:
        alert.cost_overrun(total_cost)

    # 4. Store + alert
    platform_stats = {
        p: {"raw_count": len(raw_results[p]), "scored_count": 0, "alerted_count": 0,
            "phantom_failed": len(raw_results[p]) < PHANTOM_FAILURE_THRESHOLD}
        for p in raw_results
    }
    total_alerted = 0

    for platform, count in ((p, len(r)) for p, r in raw_results.items()):
        if count < PHANTOM_FAILURE_THRESHOLD:
            alert.phantom_failure(platform, count)

    for profile in scored:
        platform = profile.get("platform", "")
        platform_stats[platform]["scored_count"] += 1

        try:
            upsert_profile(profile, run_date)
        except Exception as e:
            print(f"[main] DB write failed for {profile['profile_url']}: {e}")
            continue

        if (
            profile.get("composite_score", 0) >= SCORE_THRESHOLD
            and profile.get("matched_profile") != "none"
        ):
            try:
                alert.candidate(profile)
                platform_stats[platform]["alerted_count"] += 1
                total_alerted += 1
            except Exception as e:
                print(f"[main] Slack alert failed for {profile['profile_url']}: {e}")

    alert.weekly_summary(platform_stats, total_cost, total_alerted)
    print(f"[main] Done. {total_alerted} candidates alerted.")


if __name__ == "__main__":
    main()
