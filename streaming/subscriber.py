"""Streaming subscriber: consumes signup events from the Pub/Sub topic that
publisher.py writes to, and keeps a live running total in memory.

This is the other half of the batch-vs-streaming contrast: fct_digest_signups_daily
(the dbt mart) recomputes the day's total from scratch once a day. This process
updates its total incrementally, the instant each event arrives — no query, no
waiting for the next scheduled run.

Needs:
  GCP_PROJECT_ID, PUBSUB_SUBSCRIPTION   (see streaming/README.md)
  GOOGLE_APPLICATION_CREDENTIALS pointing at a service account key file
"""
from __future__ import annotations

import json
import os
from datetime import date

from google.cloud import pubsub_v1

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
SUBSCRIPTION_NAME = os.environ.get("PUBSUB_SUBSCRIPTION", "trendstamp-signups-sub")

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

running_total = 0
running_total_signed_in = 0
today = date.today()


def handle_message(message: pubsub_v1.subscriber.message.Message) -> None:
    global running_total, running_total_signed_in

    event = json.loads(message.data.decode("utf-8"))
    running_total += 1
    if event["is_signed_in"]:
        running_total_signed_in += 1

    print(
        f"[{today}] new signup (subscriber_id={event['subscriber_id']}, "
        f"signed_in={event['is_signed_in']}) "
        f"-> running total today: {running_total} "
        f"({running_total_signed_in} signed-in)"
    )
    message.ack()


def main() -> None:
    future = subscriber.subscribe(subscription_path, callback=handle_message)
    print(f"Listening on {subscription_path} for live signup events (Ctrl+C to stop)")
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        future.result()


if __name__ == "__main__":
    main()
