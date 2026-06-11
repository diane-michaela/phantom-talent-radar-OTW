# Phantom Talent Radar

Weekly automated candidate sourcing pipeline. PhantomBuster scrapes LinkedIn, Twitter/X, GitHub, and Reddit → Python keyword pre-filters → Claude Haiku scores each profile across 5 dimensions → SQLite stores everyone → Slack alerts for composite score ≥ 7 with a ready-to-send outreach message.

**Target geographies:** France 🇫🇷 · Spain 🇪🇸 · Portugal 🇵🇹  
**Target profiles:** frontend engineer, ML engineer, support agent, backend engineer, growth marketer, PMM  
**Run cadence:** every Monday at 8am via cron

---

## How it works

```
cron (Monday 8am)
  → main.py
      ├── run.py        — launches 4 PB phantoms, polls until done
      ├── normalise.py  — flattens each platform's JSON, keyword pre-filters
      ├── score.py      — Claude Haiku scores each profile (5 dimensions, 0–10)
      ├── db.py         — upserts into local talent_radar.db (SQLite)
      └── alert.py      — Slack blocks for score ≥ 7, phantom failures, cost overruns
```

All scored profiles are stored locally in `talent_radar.db`. Only candidates scoring ≥ 7 get a Slack ping.

---

## Scoring model

| Dimension | What it checks |
|---|---|
| Location | Physically in FR/ES/PT |
| Availability | Active job-seeking signal right now |
| Skills | Match one of the 6 target profiles |
| Authenticity | Real profile, not bot/spam |
| Language | Content in FR/ES/PT or EN |

`composite_score = average of 5 dimensions`  
**Alert threshold:** ≥ 7.0 / 10  
**Model:** `claude-haiku-4-5`, temperature 0.2  
**Estimated cost:** ~$1.30/week (300 profiles × ~1,400 tokens)

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure credentials**
```bash
cp .env.example .env
# fill in: PB_API_KEY, ANTHROPIC_API_KEY, SLACK_WEBHOOK_URL, 4 phantom IDs
```

**3. Add weekly cron**
```bash
(crontab -l 2>/dev/null; echo "0 8 * * 1 cd /path/to/talent_radar && python3 main.py >> talent_radar.log 2>&1") | crontab -
```

**4. Test a manual run**
```bash
python3 main.py
```

---

## Querying your local database

```bash
python3 query.py                               # all New candidates, score ≥ 7
python3 query.py --profile frontend_engineer
python3 query.py --min-score 6 --platform linkedin
python3 query.py --status Contacted
python3 query.py --all                         # full database
```

---

## File structure

```
talent_radar/
├── main.py          — orchestrator
├── run.py           — PhantomBuster launch + poll
├── normalise.py     — platform-specific normalisation + keyword pre-filter
├── score.py         — Claude scoring
├── db.py            — SQLite init + upsert
├── alert.py         — Slack notifications
├── query.py         — CLI query interface
├── config.py        — constants and env var loading
├── requirements.txt
└── .env.example
```

---

## PRD

Full product requirements and diagnostic: [Talent Radar SDLC PRD](https://www.notion.so/thephantomcompany/Talent-Radar-SDLC-PRD-Diagnostic-June-2026-37ad3fc42519811e920fc900c541c023)

---

## Notes

- Uses a **dedicated LinkedIn account** only — never your main or Recruiter Lite account
- Weekly cadence only — daily runs increase LinkedIn ban risk
- Raw PhantomBuster JSON is never committed (`.gitignore`) — GDPR hygiene
- `talent_radar.db` is local only — not synced or committed
- Session cookie rotation needed periodically for LinkedIn phantom
