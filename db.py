import hashlib
import sqlite3
from config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    profile_id       TEXT PRIMARY KEY,
    profile_url      TEXT UNIQUE NOT NULL,
    platform         TEXT NOT NULL,
    full_name        TEXT,
    headline         TEXT,
    location         TEXT,
    bio_text         TEXT,
    matched_profile  TEXT,
    composite_score  REAL DEFAULT 0,
    score_location   REAL,
    score_availability REAL,
    score_skills     REAL,
    score_authenticity REAL,
    score_language   REAL,
    reason           TEXT,
    outreach_draft   TEXT,
    status           TEXT DEFAULT 'New',
    first_seen       TEXT NOT NULL,
    last_seen        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS run_log (
    run_id          TEXT PRIMARY KEY,
    run_date        TEXT NOT NULL,
    platform        TEXT NOT NULL,
    raw_count       INTEGER DEFAULT 0,
    scored_count    INTEGER DEFAULT 0,
    alerted_count   INTEGER DEFAULT 0,
    token_spend_usd REAL DEFAULT 0,
    phantom_failed  INTEGER DEFAULT 0,
    errors          TEXT
);
"""


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(_SCHEMA)


def profile_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def upsert_profile(profile: dict, run_date: str):
    pid = profile_id(profile["profile_url"])
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT first_seen FROM profiles WHERE profile_id = ?", (pid,)
        ).fetchone()
        first_seen = row[0] if row else run_date
        conn.execute(
            """
            INSERT INTO profiles VALUES (
                :profile_id, :profile_url, :platform, :full_name, :headline,
                :location, :bio_text, :matched_profile, :composite_score,
                :score_location, :score_availability, :score_skills,
                :score_authenticity, :score_language, :reason, :outreach_draft,
                :status, :first_seen, :last_seen
            )
            ON CONFLICT(profile_id) DO UPDATE SET
                headline           = excluded.headline,
                bio_text           = excluded.bio_text,
                matched_profile    = excluded.matched_profile,
                composite_score    = excluded.composite_score,
                score_location     = excluded.score_location,
                score_availability = excluded.score_availability,
                score_skills       = excluded.score_skills,
                score_authenticity = excluded.score_authenticity,
                score_language     = excluded.score_language,
                reason             = excluded.reason,
                outreach_draft     = excluded.outreach_draft,
                last_seen          = excluded.last_seen
            """,
            {
                "profile_id":         pid,
                "profile_url":        profile["profile_url"],
                "platform":           profile["platform"],
                "full_name":          profile.get("full_name", ""),
                "headline":           profile.get("headline", ""),
                "location":           profile.get("location", ""),
                "bio_text":           profile.get("bio_text", ""),
                "matched_profile":    profile.get("matched_profile", "none"),
                "composite_score":    profile.get("composite_score", 0),
                "score_location":     profile.get("score_location"),
                "score_availability": profile.get("score_availability"),
                "score_skills":       profile.get("score_skills"),
                "score_authenticity": profile.get("score_authenticity"),
                "score_language":     profile.get("score_language"),
                "reason":             profile.get("reason", ""),
                "outreach_draft":     profile.get("outreach_draft", ""),
                "status":             profile.get("status", "New"),
                "first_seen":         first_seen,
                "last_seen":          run_date,
            },
        )
