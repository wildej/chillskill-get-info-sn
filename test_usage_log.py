"""
Тесты для журнала обращений и статистики.
"""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from stats import build_report
from usage_log import UsageEntry, filter_entries, log_usage, mask_user_id, mask_username, read_entries


@pytest.fixture(autouse=True)
def stable_mask_salt(monkeypatch):
    monkeypatch.setenv("USAGE_MASK_SALT", "test-mask-salt")


@pytest.fixture
def log_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "usage.log"
        monkeypatch.setenv("USAGE_LOG_PATH", str(path))
        yield path


def test_mask_username_is_deterministic():
    first = mask_username("alice", user_id=100)
    second = mask_username("bob", user_id=100)
    other = mask_username("alice", user_id=101)
    no_login = mask_username(None, user_id=100)

    assert first == second == no_login == mask_user_id(100)
    assert first != other
    assert first.startswith("m-")
    assert "alice" not in first
    assert mask_username(first) == first
    assert mask_user_id(first) == first


def test_log_and_read_entries(log_file):
    log_usage(user_id=100, username="alice", event="start")
    log_usage(
        user_id=100,
        username="alice",
        event="lookup",
        serial="0123-4567-8912",
        result="found",
    )

    raw = log_file.read_text(encoding="utf-8")
    masked = mask_user_id(100)
    assert "alice" not in raw
    data_lines = [line for line in raw.splitlines() if line and not line.startswith("timestamp\t")]
    for line in data_lines:
        parts = line.split("\t")
        assert parts[1] == masked
        assert parts[2] == masked
        assert parts[1] != "100"

    entries = read_entries(log_file)
    assert len(entries) == 2
    assert entries[0].event == "start"
    assert entries[0].user_id == masked
    assert entries[0].username == masked
    assert entries[0].username == entries[1].username
    assert entries[1].serial == "0123-4567-8912"
    assert entries[1].result == "found"


def test_filter_entries_by_period():
    entries = [
        UsageEntry(
            timestamp=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
            user_id="1",
            username="a",
            event="start",
            serial="",
            result="",
        ),
        UsageEntry(
            timestamp=datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc),
            user_id="2",
            username="b",
            event="start",
            serial="",
            result="",
        ),
    ]

    since = datetime(2026, 6, 15, tzinfo=timezone.utc)
    filtered = filter_entries(entries, since=since)
    assert len(filtered) == 1
    assert filtered[0].user_id == "2"


def test_build_report_summary():
    entries = [
        UsageEntry(
            timestamp=datetime(2026, 6, 19, 10, 0, tzinfo=timezone.utc),
            user_id="42",
            username="tester",
            event="start",
            serial="",
            result="",
        ),
        UsageEntry(
            timestamp=datetime(2026, 6, 19, 10, 1, tzinfo=timezone.utc),
            user_id="42",
            username="tester",
            event="lookup",
            serial="0123-4567-8912",
            result="found",
        ),
    ]

    report = build_report(entries, since=None, until=None)
    masked = mask_username("tester", user_id=42)
    assert "Всего обращений: 2" in report
    assert "Уникальных пользователей: 1" in report
    assert "/start: 1" in report
    assert "поиск (найден): 1" in report
    assert "SN=0123-4567-8912" in report
    assert masked in report
    assert "tester" not in report
    assert "@tester" not in report


def test_read_entries_masks_legacy_numeric_user_id(log_file):
    log_file.write_text(
        "timestamp\tuser_id\tusername\tevent\tserial\tresult\n"
        "2026-06-19T10:00:00+00:00\t100\talice\tstart\t\t\n",
        encoding="utf-8",
    )

    entries = read_entries(log_file)
    masked = mask_user_id(100)
    assert len(entries) == 1
    assert entries[0].user_id == masked
    assert entries[0].username == masked
    assert entries[0].user_id != "100"
