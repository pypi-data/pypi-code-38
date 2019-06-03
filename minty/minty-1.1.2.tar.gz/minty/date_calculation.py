from datetime import date, timedelta

import holidays
from dateutil.relativedelta import relativedelta


def add_timedelta_to_date(
    interval_type: str, time: int, starting_date: date = None
) -> date:
    """Add timedelta to given date.

    :param interval_type: type of interval
    :type interval_type: str
    :param time: time to add to date
    :type time: int
    :param starting_date: date to add time to, defaults to None
    :type starting_date: date, optional
    :raises KeyError: when interval_type does not exist.
    :return: calculated end date
    :rtype: datetime.date
    """
    if starting_date is None:
        starting_date = date.today()

    if interval_type == "days":
        end_date = starting_date + timedelta(days=time)
    elif interval_type == "business_days":
        nwd = next_business_day(starting_date)
        for _ in range(time):
            end_date = next(nwd)
    elif interval_type == "weeks":
        end_date = starting_date + timedelta(weeks=time)
    elif interval_type == "months":
        end_date = starting_date + relativedelta(months=time)
    elif interval_type == "years":
        end_date = starting_date + relativedelta(years=time)
    else:
        raise KeyError(f"Interval type: '{interval_type}' does not exist.")

    return end_date


def next_business_day(initial_date: date) -> date:
    """Calculate next business day after given date.

    :param initial_date: date to calculate from.
    :type initial_date: date
    """
    non_business_days_store = NonBusinessDays()
    date_to_check = initial_date + timedelta(days=1)
    while True:
        if date_to_check.isoweekday() not in (6, 7):
            non_business_days = non_business_days_store(date_to_check.year)
            if date_to_check not in non_business_days:
                yield date_to_check
        date_to_check = date_to_check + timedelta(days=1)


class NonBusinessDays:
    def __init__(self):
        self.store = {}

    def __call__(self, year: int):
        """Get non business days by given year.

        Checks if given year exists in `self.store` else given year will be
        initialized and stored in `self.store` for next retrieval.

        :param year: year
        :type year: int
        :return: non business days for given year
        :rtype: dict
        """
        try:
            non_business_days = self.store[year]
        except KeyError:
            self.store[year] = holidays.Netherlands(years=year)
            non_business_days = self.store[year]
        return non_business_days
