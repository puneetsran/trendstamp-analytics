"""Unit tests for streaming/publisher.py: the Supabase Realtime payload ->
Pub/Sub event mapping."""
from __future__ import annotations

import json


def realtime_payload(record: dict) -> dict:
    """Shape of a supabase postgres_changes INSERT payload."""
    return {"data": {"record": record}}


def published_event(module) -> dict:
    """Decode the JSON bytes handed to publisher.publish()."""
    (topic, data), _ = module.publisher.publish.call_args
    assert topic is module.topic_path
    return json.loads(data.decode("utf-8"))


def test_signed_in_signup_event(load_streaming):
    pub = load_streaming("publisher")
    pub.publish_signup_event(
        realtime_payload(
            {
                "id": "sub-1",
                "created_at": "2026-07-04T12:00:00Z",
                "user_id": "user-42",
                "source": "topic-drawer",
            }
        )
    )

    assert pub.publisher.publish.call_count == 1
    assert published_event(pub) == {
        "subscriber_id": "sub-1",
        "signed_up_at": "2026-07-04T12:00:00Z",
        "is_signed_in": True,
        "source": "topic-drawer",
    }


def test_anonymous_signup_event(load_streaming):
    pub = load_streaming("publisher")
    pub.publish_signup_event(
        realtime_payload(
            {"id": "sub-2", "created_at": "2026-07-04T13:00:00Z", "user_id": None}
        )
    )

    event = published_event(pub)
    assert event["is_signed_in"] is False
    assert event["source"] == ""  # missing source defaults to empty


def test_missing_user_id_key_counts_as_anonymous(load_streaming):
    pub = load_streaming("publisher")
    pub.publish_signup_event(
        realtime_payload({"id": "sub-3", "created_at": "2026-07-04T14:00:00Z"})
    )

    assert published_event(pub)["is_signed_in"] is False
