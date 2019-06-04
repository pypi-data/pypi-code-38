"""Various helper utiliites."""
import calendar
import datetime


__all__ = (
    'blind_email',
    'blind_name',
    'datetime_to_unix',
    'terbium_timestamp_to_datetime',
)


def blind_name(name, width=5):
    """Censors all but the first character of the given string."""
    if name is None:
        name = ''
    return (name[0] if name else '*').ljust(width, '*')


def blind_email(email):
    """Censors an email address."""
    if not email:
        return '*****'
    if '@' in email:
        prefix, suffix = email.split('@', 1)
        suffix = '@' + suffix
    else:
        prefix = email
        suffix = ''

    prefix = prefix[:max(1, min(3, int(len(prefix) / 2)))] + '****'
    return prefix + suffix


def datetime_to_unix(dt):
    """Returns the Unix time for the given datetime object."""
    return calendar.timegm(dt.utctimetuple())


def terbium_timestamp_to_datetime(timestamp):
    """Parses ISO 8601 compatible timestamps.

    Note: This method does not support RFC 3339.

    """
    return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
