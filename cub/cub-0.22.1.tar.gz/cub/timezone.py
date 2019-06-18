from datetime import timedelta, tzinfo


try:
    import pytz
except ImportError:
    pytz = None


ZERO = timedelta(0)


class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    def __repr__(self):
        return '<UTC>'

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return ZERO

utc = pytz.utc if pytz else UTC()
