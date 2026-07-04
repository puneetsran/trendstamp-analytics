"""Unit tests for streaming/subscriber.py: the in-memory running totals the
live consumer keeps as signup events arrive."""
from __future__ import annotations

import json
from unittest import mock


def fake_message(subscriber_id: str, is_signed_in: bool) -> mock.Mock:
    return mock.Mock(
        data=json.dumps(
            {"subscriber_id": subscriber_id, "is_signed_in": is_signed_in}
        ).encode("utf-8")
    )


def test_counts_and_acks_each_event(load_streaming):
    sub = load_streaming("subscriber")
    msg = fake_message("sub-1", is_signed_in=True)

    sub.handle_message(msg)

    assert sub.running_total == 1
    assert sub.running_total_signed_in == 1
    msg.ack.assert_called_once()


def test_anonymous_signups_only_bump_the_overall_total(load_streaming):
    sub = load_streaming("subscriber")

    sub.handle_message(fake_message("sub-1", is_signed_in=False))

    assert sub.running_total == 1
    assert sub.running_total_signed_in == 0


def test_totals_accumulate_across_events(load_streaming):
    sub = load_streaming("subscriber")

    sub.handle_message(fake_message("sub-1", is_signed_in=True))
    sub.handle_message(fake_message("sub-2", is_signed_in=False))
    sub.handle_message(fake_message("sub-3", is_signed_in=True))

    assert sub.running_total == 3
    assert sub.running_total_signed_in == 2


def test_totals_start_fresh_per_process(load_streaming):
    # Each load simulates a process start: totals begin at zero.
    sub = load_streaming("subscriber")
    assert sub.running_total == 0
    assert sub.running_total_signed_in == 0
