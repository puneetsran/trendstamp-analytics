# Streaming component

A toy real-time pipeline, contrasted with the daily batch dbt models: every new
trendstamp.com email signup is published the instant it happens and consumed by a
process that keeps a live running total, instead of waiting for the next `dbt run`.

- `publisher.py` — listens to Supabase Realtime for new rows in `digest_subscribers`,
  publishes each as a message to a Pub/Sub topic
- `subscriber.py` — consumes those messages and keeps a running count in memory,
  printing an update as each one arrives

## GCP setup (one-time, done in your own GCP account)

1. Create or pick a GCP project, and enable the **Pub/Sub API** for it
2. Create a topic: `gcloud pubsub topics create trendstamp-signups`
3. Create a subscription on that topic:
   `gcloud pubsub subscriptions create trendstamp-signups-sub --topic=trendstamp-signups`
4. Create a service account with the **Pub/Sub Editor** role, and download a JSON key
   for it (IAM & Admin -> Service Accounts -> Keys -> Add Key)

## Configure

Add to `.env` (same file the dbt pipeline uses):

```
GCP_PROJECT_ID=your-gcp-project-id
PUBSUB_TOPIC=trendstamp-signups
PUBSUB_SUBSCRIPTION=trendstamp-signups-sub
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account-key.json
```

## Run it (two terminals)

```bash
# terminal 1
set -a; source .env; set +a
.venv/bin/python streaming/subscriber.py

# terminal 2
set -a; source .env; set +a
.venv/bin/python streaming/publisher.py
```

Then sign up for the digest on trendstamp.com (or insert a test row into
`digest_subscribers`) and watch the subscriber terminal print the event live.
