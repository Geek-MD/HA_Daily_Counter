"""Reset-cycle boundary calculations."""

from datetime import datetime, timedelta

from .const import (
    RESET_CYCLE_BIMONTHLY,
    RESET_CYCLE_DAILY,
    RESET_CYCLE_HOURLY,
    RESET_CYCLE_MONTHLY,
    RESET_CYCLE_NONE,
    RESET_CYCLE_QUARTER_HOURLY,
    RESET_CYCLE_QUARTERLY,
    RESET_CYCLE_WEEKLY,
    RESET_CYCLE_YEARLY,
)

MONTH_CYCLES = {
    RESET_CYCLE_MONTHLY: 1,
    RESET_CYCLE_BIMONTHLY: 2,
    RESET_CYCLE_QUARTERLY: 3,
    RESET_CYCLE_YEARLY: 12,
}


def next_reset_time(now: datetime, cycle: str) -> datetime | None:
    """Return the next reset boundary after ``now``."""
    if cycle == RESET_CYCLE_NONE:
        return None
    if cycle == RESET_CYCLE_QUARTER_HOURLY:
        reset = now.replace(second=0, microsecond=0)
        return reset + timedelta(minutes=15 - reset.minute % 15)
    if cycle == RESET_CYCLE_HOURLY:
        return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if cycle == RESET_CYCLE_DAILY:
        return start_of_day + timedelta(days=1)
    if cycle == RESET_CYCLE_WEEKLY:
        return start_of_day + timedelta(days=7 - now.weekday())

    months_per_cycle = MONTH_CYCLES.get(cycle)
    if months_per_cycle is None:
        return start_of_day + timedelta(days=1)
    current_month_index = now.year * 12 + now.month - 1
    next_month_index = (
        current_month_index // months_per_cycle + 1
    ) * months_per_cycle
    return now.replace(
        year=next_month_index // 12,
        month=next_month_index % 12 + 1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def current_period_start(now: datetime, cycle: str) -> datetime | None:
    """Return the start of the reset period containing ``now``."""
    if cycle == RESET_CYCLE_NONE:
        return None
    if cycle == RESET_CYCLE_QUARTER_HOURLY:
        return now.replace(
            minute=now.minute - now.minute % 15, second=0, microsecond=0
        )
    if cycle == RESET_CYCLE_HOURLY:
        return now.replace(minute=0, second=0, microsecond=0)

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if cycle == RESET_CYCLE_DAILY:
        return start_of_day
    if cycle == RESET_CYCLE_WEEKLY:
        return start_of_day - timedelta(days=now.weekday())

    months_per_cycle = MONTH_CYCLES.get(cycle)
    if months_per_cycle is None:
        return start_of_day
    current_month_index = now.year * 12 + now.month - 1
    start_month_index = (
        current_month_index // months_per_cycle
    ) * months_per_cycle
    return now.replace(
        year=start_month_index // 12,
        month=start_month_index % 12 + 1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
