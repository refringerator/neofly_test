import calendar
from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils import timezone

from booking.utils import get_available_dates, available_dates_to_dict, get_user_id


def get_available_date(year: int, month: int) -> (datetime, bool, bool):
    """Получение месяца календаря и возможность выбора предыдущего и следующего"""
    current_date = timezone.localtime()
    if month and year:
        try:
            date_in_month = timezone.make_aware(datetime(year=year, month=month, day=1))
        except ValueError:
            date_in_month = current_date
    else:
        date_in_month = current_date

    # Проверка, что не менее текущего месяца
    if date_in_month < current_date:
        date_in_month = current_date

    next_month = get_first_day_in_month(current_date)
    next_plus_one = get_first_day_in_month(next_month)

    # Проверка, что не более текущего + 3
    if date_in_month > next_plus_one:
        date_in_month = next_plus_one

    first_day_in_next_month_by_cur = get_first_day_in_month(current_date)
    first_day_in_prev_month_by_selected = get_first_day_in_month(date_in_month, -1)
    first_day_in_next_month_by_selected = get_first_day_in_month(date_in_month)

    prev_month_unavailable = date_in_month < first_day_in_next_month_by_cur
    # TODO сделать проверку ближайшей доступной даты
    # else is_month_available(first_day_in_prev_month_by_selected)

    is_next_month_available = True  # TODO is_month_available(first_day_in_next_month_by_selected)

    return date_in_month, prev_month_unavailable, is_next_month_available


def available_dates_in_month(date_in_month: datetime, user_id: int) -> dict:
    """
    Получение доступных дат в месяце (с учетом кусочков предыдущего и следующего)
    Данные получаем из кэша, если их нет, то из запроса к сервису и кэшируем
    """
    redis_key = f"booking:month#{date_in_month.date().replace(day=1).isoformat()}"
    dates = cache.get(redis_key, 'has expired')
    if dates == 'has expired':
        items = get_available_dates(date_in_month, user_id=user_id)
        dates = available_dates_to_dict(items)
        cache.set(redis_key, dates, timeout=5*60)

    return dates


def is_month_available(date_in_month: datetime):
    """Проверка доступности дат месяца по наличию слотов"""
    next_month_dates = available_dates_in_month(date_in_month, 666)
    return bool(len(next_month_dates))


def get_first_day_in_month(some_date: datetime, direction: int = 1):
    days_in_month = lambda dt: calendar.monthrange(dt.year, dt.month)[1]

    middle_date = some_date.replace(day=15, hour=0, minute=0, second=0, microsecond=0, tzinfo=some_date.tzinfo)
    middle_date_in_other = middle_date + direction * timedelta(days_in_month(some_date.replace(day=15)))

    return middle_date_in_other.replace(day=1)
