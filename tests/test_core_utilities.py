from __future__ import annotations

from datetime import timezone
from unittest.mock import Mock

import pytest

from nusawall.core.events import Event
from nusawall.core.retry import retry
from nusawall.ingestion.base.raw_record import RawRecord


def test_retry_returns_value_after_transient_failure(monkeypatch):
    operation = Mock(side_effect=[OSError("temporary"), "complete"])
    sleep = Mock()
    monkeypatch.setattr("nusawall.core.retry.sleep", sleep)

    result = retry(operation, retries=2, delay=0.25)

    assert result == "complete"
    assert operation.call_count == 2
    sleep.assert_called_once_with(0.25)


def test_retry_reraises_last_error_without_extra_call_or_sleep(monkeypatch):
    operation = Mock(side_effect=OSError("persistent"))
    sleep = Mock()
    monkeypatch.setattr("nusawall.core.retry.sleep", sleep)

    with pytest.raises(OSError, match="persistent"):
        retry(operation, retries=2, delay=0.25)

    assert operation.call_count == 3
    assert sleep.call_count == 2


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"retries": -1}, "retries must be non-negative"),
        ({"delay": -0.1}, "delay must be non-negative"),
    ],
)
def test_retry_rejects_negative_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        retry(Mock(), **kwargs)


def test_event_and_raw_record_default_timestamps_are_utc_aware():
    event = Event(name="test")
    record = RawRecord(source="test", payload={})

    assert event.timestamp.tzinfo == timezone.utc
    assert record.ingest_time is not None
    assert record.ingest_time.tzinfo == timezone.utc
