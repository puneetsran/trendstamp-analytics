"""Streaming publisher: watches for new trendstamp.com digest signups in real
time (via Supabase Realtime) and publishes each one as an event to a GCP
Pub/Sub topic.

This is the "batch vs. streaming" contrast with the dbt pipeline: dbt only
sees a new signup the next time it's run (once a day). This reacts the
instant the row is inserted.

Needs:
  NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY  (from .env)
  GCP_PROJECT_ID, PUBSUB_TOPIC                             (see streaming/README.md)
  GOOGLE_APPLICATION_CREDENTIALS pointing at a service account key file
"""
from __future__ import annotations

import asyncio
import json
import os

from google.cloud import pubsub_v1
from supabase import AsyncClient, create_async_client

PUBSUB_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "trendstamp-signups")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PUBSUB_PROJECT_ID, PUBSUB_TOPIC)


def publish_signup_event(payload: dict) -> None:
    """payload is the raw Supabase Realtime postgres_changes payload."""
    new_row = payload["data"]["record"]
    event = {
        "subscriber_id": new_row["id"],
        "signed_up_at": new_row["created_at"],
        "is_signed_in": new_row.get("user_id") is not None,
        "source": new_row.get("source", ""),
    }
    future = publisher.publish(topic_path, json.dumps(event).encode("utf-8"))
    print(f"Published signup event {event['subscriber_id']} -> message id {future.result()}")


async def main() -> None:
    client: AsyncClient = await create_async_client(
        os.environ["NEXT_PUBLIC_SUPABASE_URL"],
        os.environ["NEXT_PUBLIC_SUPABASE_ANON_KEY"],
    )

    channel = client.channel("digest-subscribers-stream")
    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="digest_subscribers",
        callback=publish_signup_event,
    )
    await channel.subscribe()

    print(f"Listening for new signups on trendstamp.com -> publishing to {topic_path}")
    print("(Ctrl+C to stop)")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
