#!/usr/bin/env python3
"""
Вывод статистики использования бота и экспорт журнала запросов.

Примеры:
  python stats.py
  python stats.py --since 2026-06-01 --until 2026-06-19
  python stats.py --export report.txt
  python stats.py --since 2026-06-01 --export report.txt
"""
import argparse
from collections import Counter
from datetime import datetime, time, timezone
from pathlib import Path

from usage_log import get_log_path, iter_entries, mask_user_id, mask_username


def _parse_date(value: str, end_of_day: bool = False) -> datetime:
    dt = datetime.strptime(value, "%Y-%m-%d")
    if end_of_day:
        dt = datetime.combine(dt.date(), time(23, 59, 59))
    return dt.replace(tzinfo=timezone.utc)


def _format_local_ts(dt: datetime) -> str:
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _event_label(entry) -> str:
    if entry.event == "start":
        return "/start"
    if entry.event == "lookup":
        labels = {
            "found": "поиск (найден)",
            "not_found": "поиск (не найден)",
            "validation_failed": "поиск (ошибка формата)",
            "error": "поиск (ошибка)",
        }
        return labels.get(entry.result, f"поиск ({entry.result})")
    return entry.event


def build_report(entries, since: datetime | None, until: datetime | None) -> str:
    lines: list[str] = []
    lines.append("=== Статистика использования бота ===")

    if since or until:
        since_str = since.astimezone().strftime("%Y-%m-%d") if since else "начало"
        until_str = until.astimezone().strftime("%Y-%m-%d") if until else "сейчас"
        lines.append(f"Период: {since_str} — {until_str}")
    else:
        lines.append("Период: все записи")

    lines.append(f"Всего обращений: {len(entries)}")
    lines.append(f"Уникальных пользователей: {len({mask_user_id(e.user_id) for e in entries})}")
    lines.append("")

    event_counts = Counter(_event_label(e) for e in entries)
    if event_counts:
        lines.append("По типам событий:")
        for label, count in sorted(event_counts.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"  {label}: {count}")
        lines.append("")

    lines.append("=== Журнал запросов ===")
    if not entries:
        lines.append("(нет записей за выбранный период)")
    else:
        for entry in entries:
            user = mask_username(entry.username, user_id=entry.user_id)
            ts = _format_local_ts(entry.timestamp)
            detail = _event_label(entry)
            if entry.serial:
                detail += f", SN={entry.serial}"
            lines.append(f"{ts} | {user} | {detail}")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Статистика использования Telegram-бота по журналу обращений.",
    )
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Начало периода (включительно, UTC)",
    )
    parser.add_argument(
        "--until",
        metavar="YYYY-MM-DD",
        help="Конец периода (включительно, UTC)",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Сохранить отчёт в текстовый файл (иначе вывод в stdout)",
    )
    parser.add_argument(
        "--log",
        metavar="PATH",
        help="Путь к журналу (по умолчанию USAGE_LOG_PATH или data/usage.log)",
    )
    args = parser.parse_args()

    since = _parse_date(args.since) if args.since else None
    until = _parse_date(args.until, end_of_day=True) if args.until else None
    log_path = Path(args.log) if args.log else get_log_path()

    if not log_path.exists():
        parser.error(f"Журнал не найден: {log_path}")

    entries = list(iter_entries(log_path, since=since, until=until))
    report = build_report(entries, since=since, until=until)

    if args.export:
        export_path = Path(args.export)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(report, encoding="utf-8")
        print(f"Отчёт сохранён: {export_path} ({len(entries)} записей)")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
