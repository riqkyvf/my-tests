from datetime import date, datetime, timedelta, timezone

from config import DEFAULT_PROFILE_TIMEZONE

MOSCOW_TIMEZONE = timezone(timedelta(hours=3), DEFAULT_PROFILE_TIMEZONE)


def now_in_moscow() -> datetime:
    return datetime.now(timezone.utc).astimezone(MOSCOW_TIMEZONE)


def today_in_moscow() -> date:
    return now_in_moscow().date()


MONTHS_RU = {
    1: "янв.",
    2: "февр.",
    3: "мар.",
    4: "апр.",
    5: "мая",
    6: "июн.",
    7: "июл.",
    8: "авг.",
    9: "сент.",
    10: "окт.",
    11: "нояб.",
    12: "дек.",
}


def format_slot_date(slot_day: date) -> str:
    return f"{slot_day.day} {MONTHS_RU[slot_day.month]}"
