"""
Quick query interface for talent_radar.db.

Usage:
    python query.py                          # all candidates with score >= 7, status New
    python query.py --profile frontend_engineer
    python query.py --min-score 6 --platform linkedin
    python query.py --status New --limit 20
    python query.py --all                    # everything in the DB
"""
import argparse
import sqlite3
from config import DB_PATH


def query(profile=None, min_score=7.0, platform=None, status=None, limit=50, show_all=False):
    if not show_all and status is None:
        status = "New"
    if show_all:
        min_score = 0

    conditions = ["composite_score >= :min_score"]
    params = {"min_score": min_score, "limit": limit}

    if profile:
        conditions.append("matched_profile = :profile")
        params["profile"] = profile
    if platform:
        conditions.append("platform = :platform")
        params["platform"] = platform
    if status:
        conditions.append("status = :status")
        params["status"] = status

    sql = f"""
        SELECT full_name, platform, matched_profile, composite_score,
               location, headline, reason, outreach_draft, profile_url, status, first_seen
        FROM profiles
        WHERE {' AND '.join(conditions)}
        ORDER BY composite_score DESC
        LIMIT :limit
    """

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()

    if not rows:
        print("No candidates found.")
        return

    for r in rows:
        print(f"\n{'='*60}")
        print(f"{r['full_name']} [{r['platform']}] — {r['matched_profile']} — score {r['composite_score']:.1f}/10")
        print(f"📍 {r['location']} | {r['headline']}")
        print(f"Why: {r['reason']}")
        if r["outreach_draft"]:
            print(f"\nOutreach:\n{r['outreach_draft']}")
        print(f"\n{r['profile_url']}  (status: {r['status']}, first seen: {r['first_seen']})")

    print(f"\n{len(rows)} candidate(s) returned.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--profile",   help="e.g. frontend_engineer")
    p.add_argument("--min-score", type=float, default=7.0)
    p.add_argument("--platform",  help="linkedin | twitter | github | reddit")
    p.add_argument("--status",    help="New | Contacted | No response | Replied | Hired")
    p.add_argument("--limit",     type=int, default=50)
    p.add_argument("--all",       action="store_true", dest="show_all")
    args = p.parse_args()
    query(
        profile=args.profile,
        min_score=args.min_score,
        platform=args.platform,
        status=args.status,
        limit=args.limit,
        show_all=args.show_all,
    )
