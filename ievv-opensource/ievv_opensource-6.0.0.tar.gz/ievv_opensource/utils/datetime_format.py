import arrow
from django.conf import settings
from django.template import defaultfilters


def format_datetime_in_timezone(datetime_object, datetime_format='DATETIME_FORMAT', timezone=settings.TIME_ZONE):
    """
    Format a datetime object in a timezone.

    Args:
        datetime_object (datetime.datetime): Datetime object to format.
        datetime_format (str): A Django datetime formatting string name, such as ``"DATETIME_FORMAT"``,
            ``"SHORT_DATETIME_FORMAT``", ``"DATE_FORMAT"``, ...
        timezone (str): Defaults to ``settings.TIME_ZONE``. The datetime is converted to
            this timezone. So if you use UTC in the database, and want to present another
            timezone, this will convert it correctly.

    Returns:
        str: The formatted datetime.
    """
    return defaultfilters.date(arrow.get(datetime_object).to(timezone).datetime, datetime_format)
