"""Shared fixture for loading the streaming modules under test.

publisher.py and subscriber.py create their GCP Pub/Sub clients at import
time, so each test loads a fresh copy of the module with those clients
patched out (fresh copies also reset the subscriber's module-level running
totals between tests).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def load_streaming(monkeypatch):
    def _load(name: str):
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
        with mock.patch("google.cloud.pubsub_v1.PublisherClient"), mock.patch(
            "google.cloud.pubsub_v1.SubscriberClient"
        ):
            spec = importlib.util.spec_from_file_location(
                f"streaming_{name}_under_test", REPO_ROOT / "streaming" / f"{name}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module

    return _load
