"""
Журнал обращений к боту.

Формат файла — TSV с заголовком:
timestamp	user_id	username	event	serial	result

user_id и username в журнале — детерминированная маска (HMAC), а не данные Telegram.
"""
import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOG_PATH = Path("data/usage.log")
LOG_HEADER = "timestamp\tuser_id\tusername\tevent\tserial\tresult\n"

_MASK_PREFIX = "m-"
_MASK_HEX_LEN = 12
_MASKED_RE = re.compile(rf"^{_MASK_PREFIX}[0-9a-f]{{{_MASK_HEX_LEN}}}$")
_DEFAULT_MASK_SALT = "chillskill-usage-mask-v1"


def _mask_key() -> bytes:
    salt = os.getenv("USAGE_MASK_SALT") or os.getenv("BOT_TOKEN") or _DEFAULT_MASK_SALT
    return salt.encode("utf-8")


def _is_masked(value: str) -> bool:
    return bool(_MASKED_RE.fullmatch(value))


def _hmac_mask(material: str) -> str:
    digest = hmac.new(_mask_key(), material.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{_MASK_PREFIX}{digest[:_MASK_HEX_LEN]}"


def mask_user_id(user_id: int | str) -> str:
    """Статическая маска Telegram user_id. Уже замаскированное значение не хешируется повторно."""
    raw = str(user_id).strip()
    if not raw:
        return ""
    if _is_masked(raw):
        return raw
    return _hmac_mask(f"tg:{raw}")


def mask_username(username: str | None, user_id: int | str | None = None) -> str:
    """Статическая маска: один и тот же пользователь всегда даёт одну и ту же строку.

    Идентичность берётся по Telegram user_id (логин может меняться и не пишется в журнал).
    Если user_id нет — маскируется сам username. Уже замаскированное значение не хешируется повторно.
    """
    if user_id is not None and str(user_id).strip():
        return mask_user_id(user_id)

    raw = (username or "").strip()
    if not raw:
        return ""
    if _is_masked(raw):
        return raw
    return _hmac_mask(f"name:{raw.casefold()}")


def get_log_path() -> Path:
    """Путь к файлу журнала (переменная USAGE_LOG_PATH или data/usage.log)."""
    raw = os.getenv("USAGE_LOG_PATH")
    return Path(raw) if raw else DEFAULT_LOG_PATH


@dataclass(frozen=True)
class UsageEntry:
    timestamp: datetime
    user_id: str
    username: str
    event: str
    serial: str
    result: str


def _ensure_log_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(LOG_HEADER, encoding="utf-8")


def log_usage(
    *,
    user_id: int,
    username: str | None,
    event: str,
    serial: str = "",
    result: str = "",
) -> None:
    """Добавляет запись в журнал обращений."""
    path = get_log_path()
    _ensure_log_file(path)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    safe_user_id = mask_user_id(user_id)
    safe_username = mask_username(username, user_id=user_id)
    safe_serial = serial.replace("\t", " ").replace("\n", " ")
    safe_result = result.replace("\t", " ").replace("\n", " ")

    line = f"{ts}\t{safe_user_id}\t{safe_username}\t{event}\t{safe_serial}\t{safe_result}\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def _parse_timestamp(raw: str) -> datetime:
    if raw.endswith("+0000"):
        raw = raw[:-5] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def read_entries(path: Path | None = None) -> list[UsageEntry]:
    """Читает все записи из журнала."""
    log_path = path or get_log_path()
    if not log_path.exists():
        return []

    entries: list[UsageEntry] = []
    with log_path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line or line.startswith("timestamp\t"):
                continue
            parts = line.split("\t")
            if len(parts) != 6:
                raise ValueError(f"Некорректная строка {line_no} в {log_path}: {line!r}")
            entries.append(
                UsageEntry(
                    timestamp=_parse_timestamp(parts[0]),
                    user_id=mask_user_id(parts[1]),
                    username=mask_username(parts[2], user_id=parts[1]),
                    event=parts[3],
                    serial=parts[4],
                    result=parts[5],
                )
            )
    return entries


def filter_entries(
    entries: list[UsageEntry],
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[UsageEntry]:
    """Фильтрует записи по периоду [since, until]."""
    result: list[UsageEntry] = []
    for entry in entries:
        if since and entry.timestamp < since:
            continue
        if until and entry.timestamp > until:
            continue
        result.append(entry)
    return result


def iter_entries(
    path: Path | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> Iterator[UsageEntry]:
    """Итератор по записям журнала с опциональной фильтрацией по дате."""
    yield from filter_entries(read_entries(path), since=since, until=until)
