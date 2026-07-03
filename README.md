# trendstamp-analytics

A dbt analytics pipeline that reads [trendstamp.com](https://www.trendstamp.com)'s real Supabase
data and builds daily rollups: topic rotation and rank history, and digest signup growth.

## Setup

```bash
# 1. Python env (use a real Python, not a bleeding-edge one dbt hasn't caught up to)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Create the scoped database role (once, in Supabase's SQL Editor)
#    Run scripts/setup_db_role.sql there first.

# 3. Configure connection
cp .env.example .env   # fill in SUPABASE_DB_HOST / SUPABASE_DB_PASSWORD from step 2
```

## Run the dbt pipeline

```bash
cd dbt
export DBT_PROFILES_DIR=.
set -a; source ../.env; set +a
dbt debug   # confirms the connection works before anything else
dbt run     # builds staging views + mart tables in the analytics schema
dbt test    # runs the not_null/unique tests defined in models/staging/_sources.yml
```

## What's here

| Path | What |
|---|---|
| `dbt/models/staging/` | 1:1 views over trendstamp.com's production tables (`topic_snapshots`, `digest_subscribers`, `topic_follows`) |
| `dbt/models/marts/` | Real rollups: daily topic/rank rotation, daily signup growth with a cumulative window function |
| `scripts/setup_db_role.sql` | Creates the low-privilege `dbt_analytics` role — run once in Supabase |
| `orchestration/definitions.py` | Dagster job + daily schedule that runs the dbt pipeline |
| `streaming/` | Real-time signup event pipeline (Supabase Realtime -> GCP Pub/Sub), contrasted with the daily batch dbt models — see `streaming/README.md` |

## Orchestration

```bash
cd .. # back to project root
.venv/bin/dagster dev -f orchestration/definitions.py
```

Opens a local UI to trigger a manual run or watch the daily 9am schedule.

## Status

- [x] dbt project scaffolded against real schema
- [x] Staging models for all 3 production tables
- [x] Two mart models with tests
- [x] Verified end-to-end against the real database (5/5 models, 10/10 tests passing)
- [x] Dagster orchestrator with a daily schedule
- [x] Streaming component (Supabase Realtime -> GCP Pub/Sub, live running total) — code written, needs your GCP setup to run for real (see `streaming/README.md`)
- [ ] Cost-optimization pass writeup on the underlying GCP project
