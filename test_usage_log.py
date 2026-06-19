"""
Тесты для журнала обращений и статистики.
"""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from stats import build_report
from usage_log import UsageEntry, filter_entries, log_usage, read_entries


@pytest.fixture
def log_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "usage.log"
        monkeypatch.setenv("USAGE_LOG_PATH", str(path))
        yield path


def test_log_and_read_entries(log_file):
    log_usage(user_id=100, username="alice", event="start")
    log_usage(
        user_id=100,
        username="alice",
        event="lookup",
        serial="0123-4567-8912",
        result="found",
    )

    entries = read_entries(log_file)
    assert len(entries) == 2
    assert entries[0].event == "start"
    assert entries[1].serial == "0123-4567-8912"
    assert entries[1].result == "found"


def test_filter_entries_by_period():
    entries = [
        UsageEntry(
            timestamp=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
            user_id=1,
            username="a",
            event="start",
            serial="",
            result="",
        ),
        UsageEntry(
            timestamp=datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc),
            user_id=2,
            username="b",
            event="start",
            serial="",
            result="",
        ),
    ]

    since = datetime(2026, 6, 15, tzinfo=timezone.utc)
    filtered = filter_entries(entries, since=since)
    assert len(filtered) == 1
    assert filtered[0].user_id == 2


def test_build_report_summary():
    entries = [
        UsageEntry(
            timestamp=datetime(2026, 6, 19, 10, 0, tzinfo=timezone.utc),
            user_id=42,
            username="tester",
            event="start",
            serial="",
            result="",
        ),
        UsageEntry(
            timestamp=datetime(2026, 6, 19, 10, 1, tzinfo=timezone.utc),
            user_id=42,
            username="tester",
            event="lookup",
            serial="0123-4567-8912",
            result="found",
        ),
    ]

    report = build_report(entries, since=None, until=None)
    assert "Всего обращений: 2" in report
    assert "Уникальных пользователей: 1" in report
    assert "/start: 1" in report
    assert "поиск (найден): 1" in report
    assert "SN=0123-4567-8912" in report
