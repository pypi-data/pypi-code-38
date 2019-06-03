import iso8601


def datetime_to_utc_datetime_iso8601(datetime, day_granularity=False):
    """ Convert a datetime into its iso8601 UTC date.

        Parameters:
            datetime: Datetime to convert.
            day_granularity: Apply the day granularity

        Returns:
            Converted date (string).

    """
    # ignore microseconds
    datetime = datetime.replace(microsecond=0)
    result = datetime.isoformat() + 'Z'
    if day_granularity:
        result = result[:-10]
    return result


def utc_datetime_iso8601_to_datetime(utc_datetime):
    """ Convert an iso8601 UTC date into datetime.

        Parameters:
            utc_datetime: iso8601 UTC date to convert.

        Returns:
            Converted date (Datetime).

    """
    return iso8601.parse_date(utc_datetime).replace(tzinfo=None)

