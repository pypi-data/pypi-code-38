# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta, time, datetime
from Shahi.algorithms import get_gregorian_date_from_julian_day
import Shahi
from Shahi import ShahiDate
from Shahi import MAXYEAR, MINYEAR, SATURDAY
from Shahi.formatting import ShahiDatetimeFormatter, AM_PM, AM_PM_ASCII
from Shahi.helpers import force_encoded_string_output


__author__ = 'shah'


class ShahiDatetime(ShahiDate):
    """
    Inherited from :py:class:`Shahi.ShahiDate`.

    Represent a moment in :doc:`/persiancalendar`.

    The first parameter can be an integer,
    :py:class:`datetime.date`, :py:class:`Shahi.ShahiDate`,
    :py:class:`datetime.datetime` or :py:class:`Shahi.ShahiDatetime`.

    You may create this object by passing `julian_day` parameter.


    :param year: Shahi year
    :param month: 1-12
    :param day: 1-31
    :param hour: 0-23
    :param minute: 0-59
    :param second: 0-59
    :param microsecond: 0-999999
    :param tzinfo: Timezone info
    :param julian_day:

    :type year: :py:class:`int` | :py:class:`datetime.date` | :py:class:`Shahi.ShahiDate`
    :type month: int
    :type day: int
    :type hour: int
    :type minute: int
    :type second: int
    :type microsecond: int
    :type tzinfo: :py:class:`datetime.tzinfo` | callable
    :type julian_day: int


    :return: An object representing a moment persian calendar.
    :rtype: :py:class:`Shahi.ShahiDatetime`

    """

    #: Represent the earlier moment which supported by this class.
    min = (MINYEAR, 1, 1)

    #: Represent the last moment which supported by this class.
    max = (MAXYEAR, 12, 29, 23, 59, 59, 999999)

    resolution = timedelta(microseconds=1)

    def __init__(self, year=1, month=1, day=1, hour=0, minute=0, second=0,
                 microsecond=0, tzinfo=None, julian_day=None):

        if callable(tzinfo):
            tzinfo = tzinfo()

        if isinstance(year, ShahiDatetime):
            year, month, day, hour, minute, second, microsecond = \
                year.year, year.month, year.day, year.hour, year.minute, year.second, year.microsecond

        elif isinstance(year, datetime):
            hour, minute, second, microsecond = year.hour, year.minute, year.second, year.microsecond
            if not tzinfo:
                tzinfo = year.tzinfo

        ShahiDate.__init__(self, year=year, month=month, day=day, julian_day=julian_day)
        self._time = time(hour, minute, second, microsecond, tzinfo)

    ##############
    # Properties #
    ##############

    @property
    def hour(self):
        """
        :getter: Returns the hour
        :type: int
        """
        return self._time.hour

    @property
    def minute(self):
        """
        :getter: Returns the minute
        :type: int
        """
        return self._time.minute

    @property
    def second(self):
        """
        :getter: Returns the second
        :type: int
        """
        return self._time.second

    @property
    def microsecond(self):
        """
        :getter: Returns the microsecond
        :type: int
        """
        return self._time.microsecond

    @property
    def tzinfo(self):
        """
        :getter: Returns the timezone info
        :type: :py:class:`datetime.tzinfo`
        """
        return self._time.tzinfo

    @classmethod
    def formatterfactory(cls, fmt):
        """
        Creates the appropriate formatter for this type.

        :param fmt: str The format string
        :return: The new formatter instance.
        :rtype: :py:class:`Shahi.formatting.ShahiDatetimeFormatter`
        """
        return ShahiDatetimeFormatter(fmt)

    @classmethod
    def now(cls, tz=None):
        """
        If optional argument tz is :py:obj:`None` or not specified, this is like today(), but,
        if possible, supplies more precision than can be gotten from going through a
        :py:func:`time.time()` timestamp (for example,
        this may be possible on platforms supplying the C gettimeofday() function).

        Else tz must be an instance of a :py:class:`datetime.tzinfo` subclass,
        and the current date and time are converted to tz's time zone.
        In this case the result is equivalent to `tz.fromutc(ShahiDatetime.utcnow().replace(tzinfo=tz))`.
        See also :py:meth:`Shahi.ShahiDate.today` and :py:meth:`Shahi.ShahiDatetime.utcnow`.

        :param tz: :py:class:`datetime.tzinfo` The optional timezone to get current local date & time.
        :return: the current local date and time
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        return cls(datetime.now(tz))

    @classmethod
    def utcnow(cls):
        """
        This is like :py:meth:`Shahi.ShahiDatetime.now`, but returns the current
        UTC date and time, as a naive datetime object.

        :return: The current UTC date and time, with tzinfo None.
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        return cls(datetime.utcnow())

    @classmethod
    def fromtimestamp(cls, timestamp, tz=None):
        """
        Creates a new :py:class:`Shahi.ShahiDatetime` instance from the given posix timestamp.

        If optional argument tz is :py:obj:`None` or not specified, the timestamp is converted to
        the platform's local date and time, and the returned datetime object is naive.

        Else tz must be an instance of a class :py:class:`datetime.tzinfo` subclass,
        and the timestamp is converted to tz's time zone. In this case the result is
        equivalent to `tz.fromutc(ShahiDatetime.utcfromtimestamp(timestamp).replace(tzinfo=tz))`.

        This method may raise `ValueError`, if the timestamp is out of the range of values
        supported by the platform C localtime() or gmtime() functions.
        It's common for this to be restricted to years in 1970 through 2038.

        Note that on non-POSIX systems that include leap seconds in their
        notion of a timestamp, leap seconds are ignored by fromtimestamp(), and then
        it's possible to have two timestamps differing by a second that yield
        identical datetime objects. See also :py:class:`Shahi.ShahiDatetime.utcfromtimestamp`.

        .. testsetup:: api-datetime-fromtimestamp

            import Shahi
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-fromtimestamp

            >>> ShahiDatetime.fromtimestamp(1313132131.21232)
            Shahi.ShahiDatetime(1390, 5, 21, 11, 25, 31, 212320, Jomeh)

        :param timestamp: float the posix timestamp, i.e 1014324234.23423423.
        :param tz: :py:class:`datetime.tzinfo` The optional timezone to get local date & time from the given timestamp.
        :return: The local date and time corresponding to the POSIX timestamp, such as is returned by :py:func:`time.time()`.
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        return cls(datetime.fromtimestamp(timestamp, tz=tz))

    @classmethod
    def utcfromtimestamp(cls, timestamp):
        """
        This may raise ValueError, if the timestamp is
        out of the range of values supported by the platform C gmtime()
        function. It's common for this to be restricted to years in 1970
        through 2038. See also :py:meth:`Shahi.ShahiDatetime.fromtimestamp`.

        :return: The UTC datetime corresponding to the POSIX timestamp,
                with tzinfo None.

        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        return cls(datetime.utcfromtimestamp(timestamp))

    @classmethod
    def fromordinal(cls, ordinal):
        """
        Return the Shahi datetime corresponding to the proleptic Shahi ordinal,
        where Farvardin 1 of year 1 has ordinal 1. ValueError is
        raised unless 1 <= ordinal <= ShahiDatetime.max.toordinal(). The hour, minute, second
        and microsecond of the result are all 0, and tzinfo is None.
        """
        return cls.min + timedelta(days=ordinal - 1)

    @classmethod
    def combine(cls, date, _time):
        """
        Return a new Shahi datetime object whose date members are equal to the given date object's, and whose _time
        and tzinfo members are equal to the given _time object's.
        For any datetime object d, d == datetime.combine(d.date(), d.timetz()). If date is a datetime object, its _time
        and tzinfo members are ignored.

        :param date: :py:class:`Shahi.ShahiDate` the date object to combine.
        :param _time: :py:class:`datetime.time` the time object to combine.
        :return: the combined Shahi date & time object.
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        if isinstance(date, (ShahiDatetime, Shahi.ShahiDate)):
            date = date.todate()
        return cls(datetime.combine(date, _time))

    @classmethod
    def strptime(cls, date_string, fmt):
        """
        Return a :py:class:`Shahi.ShahiDatetime` corresponding to *date_string*, parsed according to format.

        ValueError is raised if the *date_string* and format can’t be parsed with
        :py:class:`Shahi.formatting.ShahiDatetimeFormatter` instance returned by
        :py:meth:`Shahi.ShahiDatetime.formatterfactory` method.

        :param date_string: str The representing date & time in specified format.
        :param fmt: str The format string.
        :return: Shahi datetime object.
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        result = cls.formatterfactory(fmt).parse(date_string)
        result = {
            k: v for k, v in result.items() if k in (
                'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo'
            )
        }
        return cls(**result)

    def todatetime(self):
        """
        Converts the current instance to the python builtins :py:class:`datetime.datetime` instance.

        :return: the new :py:class:`datetime.datetime` instance representing the current date and time in gregorian calendar.
        :rtype: :py:class:`datetime.datetime`
        """
        arr = get_gregorian_date_from_julian_day(self.tojulianday())
        return datetime(int(arr[0]), int(arr[1]), int(arr[2]), self.hour, self.minute, self.second, self.microsecond,
                        self.tzinfo)

    def date(self):
        """
        Return date object with same year, month and day.

        :rtype: :py:class:`Shahi.ShahiDate`
        """
        return Shahi.ShahiDate(self.year, self.month, self.day)

    def time(self):
        """
        Return time object with same hour, minute, second and microseconds. tzinfo is :py:obj:`None`. See also
        method :py:meth:`Shahi.ShahiDatetime.timetz()`.

        :rtype: :py:class:`datetime.time`
        """
        return time(self.hour, self.minute, self.second, self.microsecond)

    def timetz(self):
        """
        Return time object with same hour, minute, second, microsecond, and tzinfo attributes. See also
        method :py:meth:`Shahi.ShahiDatetime.time()`.

        :rtype: :py:class:`datetime.time`
        """
        return time(self.hour, self.minute, self.second, self.microsecond, self.tzinfo)

    def replace(self, year=None, month=None, day=None, hour=None,
                minute=None, second=None, microsecond=None, tzinfo=None):
        """
        Return a :py:class:`Shahi.ShahiDatetime` instance with the same attributes, except for those attributes
        given new values by whichever keyword arguments are specified. Note that tzinfo=None can be specified to create
        a naive datetime from an aware datetime with no conversion of date and time data, without adjusting the date
        the and time based tzinfo.

        :param year: int
        :param month: int
        :param day: int
        :param hour: int
        :param minute: int
        :param second: int
        :param microsecond: int
        :param tzinfo: :py:class:`datetime.tzinfo`
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        year, month, day = self._validate(
            year if year else self.year,
            month if month else self.month,
            day if day else self.day
        )

        result = ShahiDatetime(
            year,
            month,
            day,
            self.hour if hour is None else hour,
            self.minute if minute is None else minute,
            self.second if second is None else second,
            self.microsecond if microsecond is None else microsecond,
            tzinfo if tzinfo != self.tzinfo else self.tzinfo
        )
        return result

    def astimezone(self, tz):
        """
        Return a :py:class:`Shahi.ShahiDatetime` object with new :py:meth:`Shahi.ShahiDatetime.tzinfo` attribute
        tz, adjusting the date and time data so the result is the same UTC time as self, but in *tz*‘s local time.

        *tz* must be an instance of a :py:class:`datetime.tzinfo` subclass, and
        its :py:meth:`datetime.tzinfo.utcoffset()` and :py:meth:`datetime.tzinfo.dst()` methods must not
        return :py:obj:`None`. *self* must be aware (`self.tzinfo` must not be `None`, and `self.utcoffset()` must
        not return `None`).

        If `self.tzinfo` is `tz`, `self.astimezone(tz)` is equal to `self`: no adjustment of date or time data is
        performed. Else the result is local time in time zone `tz`, representing the same UTC time as `self`:
        after `astz = dt.astimezone(tz), astz - astz.utcoffset()` will usually have the same date and time data as
        `dt - dt.utcoffset()`. The discussion of class :py:class:`datetime.tzinfo` explains the cases at Daylight
        Saving Time transition boundaries where this cannot be achieved (an issue only if `tz` models both
        standard and daylight time).

        If you merely want to attach a time zone object `tz` to a datetime dt without adjustment of date and time data,
        use `dt.replace(tzinfo=tz)`. If you merely want to remove the time zone object from an aware datetime dt
        without conversion of date and time data, use `dt.replace(tzinfo=None)`.

        Note that the default :py:meth:`datetime.tzinfo.fromutc()` method can be overridden in a
        :py:class:`datetime.tzinfo` subclass to affect the result returned
        by :py:meth:`Shahi.ShahiDatetime.astimezone()`. Ignoring error
        cases, :py:meth:`Shahi.ShahiDatetime.astimezone()` acts like:

        .. code-block:: python
           :emphasize-lines: 3,5

           def astimezone(self, tz):  # doctest: +SKIP

               if self.tzinfo is tz:
                   return self
               if self.tzinfo:
                   utc = self - self.utcoffset()
               else:
                   utc = self
               return tz.fromutc(utc.replace(tzinfo=tz))


        :param tz: :py:class:`datetime.tzinfo`
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        if self.tzinfo is tz:
            return self
        if self.tzinfo:
            utc = self - self.utcoffset()
        else:
            utc = self
        return tz.fromutc(utc.replace(tzinfo=tz))

    def utcoffset(self):
        """
        If :py:meth:`Shahi.ShahiDatetime.tzinfo` is :py:obj:`None`, returns :py:obj:`None`, else
        returns `self.tzinfo.utcoffset(self)`, and raises an exception if the latter doesn’t return :py:obj:`None`,
        or a :py:class:`datetime.timedelta` object representing a whole number of minutes with magnitude less than one
        day.

        :rtype: :py:class:`datetime.timedelta`
        """
        if self.tzinfo:
            return self.tzinfo.utcoffset(self)
        else:
            return None

    def dst(self):
        """
        If :py:meth:`Shahi.ShahiDatetime.tzinfo` is :py:obj:`None`, returns :py:obj:`None`, else returns
        `self.tzinfo.dst(self)`, and raises an exception if the latter doesn’t return :py:obj:`None`, or
        a :py:class:`datetime.timedelta` object representing a whole number of minutes with magnitude less than one day.

        :rtype: :py:class:`datetime.timedelta`
        """
        if self.tzinfo:
            return self.tzinfo.dst(self)
        else:
            return None

    def tzname(self):
        """
        If :py:meth:`Shahi.ShahiDatetime.tzinfo` is :py:obj:`None`, returns :py:obj:`None`, else returns
        `self.tzinfo.tzname(self)`, raises an exception if the latter doesn’t return:py:obj:`None`or a string object.

        :rtype: str
        """
        if self.tzinfo:
            return self.tzinfo.tzname(self)
        else:
            return None

    @staticmethod
    def _ensure_Shahi_datetime(x):
        if not isinstance(x, ShahiDatetime):
            raise TypeError('Comparison just allow with ShahiDatetime')

    def copy(self):
        """

        It's equivalent to:

        .. testsetup:: api-datetime-copy

            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-copy

            >>> source_date = ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999)
            >>> ShahiDatetime(source_date.year, source_date.month, source_date.day, source_date.hour, source_date.minute, source_date.second, source_date.microsecond)
            Shahi.ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999, Yekshanbeh)

        :return: A Copy of the current instance.
        :rtype: :py:class:`Shahi.ShahiDatetime`
        """
        return ShahiDatetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second, self.microsecond,
            tzinfo=self.tzinfo
        )

    def isoformat(self, sep='T'):
        """
        Return a string representing the date and time in ISO 8601 format, YYYY-MM-DDTHH:MM:SS.mmmmmm or, if
        microsecond is 0, YYYY-MM-DDTHH:MM:SS

        If utcoffset() does not return :py:obj:`None`, a 6-character string is appended, giving the UTC offset in (signed) hours
        and minutes: YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM or, if microsecond is 0 YYYY-MM-DDTHH:MM:SS+HH:MM

        :param sep: str The separator between date & time.
        :return: The ISO formatted date & time.
        :rtype: str
        """
        return self.strftime('%Y-%m-%d' + sep + '%H:%M:%S.%f%z')

    def localshortformat(self):
        """
        Return a string representing the date and time in preserved format: `%a %d %b %y %H:%M`.

        .. testsetup:: api-datetime-localshortformat

            from __future__ import print_function
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-localshortformat

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999).localshortformat())
            ی 24 خر 94 10:02

        :return: The local short formatted date & time string.
        :rtype: str
        """
        return self.strftime('%a %d %b %y %H:%M')

    def localshortformatascii(self):
        """
        Return a string representing the date and time in preserved format: `%e %d %g %y %H:%M`.

        .. testsetup:: api-datetime-localshortformatascii

            from __future__ import print_function
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-localshortformatascii

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999).localshortformatascii())
            Y 24 Kh 94 10:02

        :return: The local short ascii formatted date & time string.
        :rtype: str
        """

        return self.strftime('%e %d %g %y %H:%M')

    def localdatetimeformat(self):
        """
        Return a string representing the date and time in preserved format: `%A %d %B %Y %I:%M:%S %p`.

        .. testsetup:: api-datetime-localdatetimeformat

            from __future__ import print_function
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-localdatetimeformat

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999).localdatetimeformat())
            یکشنبه 24 خرداد 1394 10:02:03 ق.ظ

        :return: The local formatted date & time string.
        :rtype: str
        """

        return self.strftime('%A %d %B %Y %I:%M:%S %p')

    def localdatetimeformatascii(self):
        """
        Return a string representing the date and time in preserved format: `%E %d %G %Y %I:%M:%S %t`.

        .. testsetup:: api-datetime-localdatetimeformatascii

            from __future__ import print_function
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-localdatetimeformatascii

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999).localdatetimeformatascii())
            Yekshanbeh 24 Khordad 1394 10:02:03 AM

        :return: The local ascii formatted date & time string.
        :rtype: str
        """
        return self.strftime('%E %d %G %Y %I:%M:%S %t')

    def localtimeformat(self):
        """
        Return a string representing the date and time in preserved format: `%I:%M:%S %p`.

        .. testsetup:: api-datetime-localtimeformat

            from __future__ import print_function
            from Shahi import ShahiDatetime

        .. doctest:: api-datetime-localtimeformat

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999).localtimeformat())
            10:02:03 ق.ظ

        :return: The local formatted time string.
        :rtype: str
        """
        return self.strftime('%I:%M:%S %p')

    def hour12(self):
        """
        Return The hour value between `1-12`. use :py:meth:`Shahi.ShahiDatetime.ampm()` or
        :py:meth:`Shahi.ShahiDatetime.ampmascii()` to determine `ante meridiem` and or `post meridiem`

        :rtype: int
        """
        res = self.hour
        if res > 12:
            res -= 12
        elif res == 0:
            res = 12
        return res

    def ampm(self):
        """

        :rtype: str
        :return: The 'ق.ظ' or 'ب.ظ' to determine `ante meridiem` and or `post meridiem`
        """
        if self.hour < 12:
            return AM_PM[0]
        return AM_PM[1]

    def ampmascii(self):
        """

        :rtype: str
        :return: The 'AM' or 'PM' to determine `ante meridiem` and or `post meridiem`
        """
        if self.hour < 12:
            return AM_PM_ASCII[0]
        return AM_PM_ASCII[1]

    def utcoffsetformat(self):
        """

        .. testsetup:: api-datetime-utcoffsetformat

            from __future__ import def copy
            from Shahi import ShahiDatetime, TehranTimezone

        .. doctest:: api-datetime-utcoffsetformat

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999, tzinfo=TehranTimezone).utcoffsetformat())
            04:30

        :return: The formatted(*HH:MM*) time representing offset from UTC.
        :rtype: str
        """
        if self.tzinfo:
            td = self.utcoffset()
            _minutes = td.seconds / 60
            hours = _minutes / 60
            minutes = _minutes % 60
            return '%02d:%02d' % (hours, minutes)
        return ''

    def tznameformat(self):
        """
        If :py:meth:`Shahi.ShahiDatetime.tzinfo` is :py:obj:`None`, returns empty string, else returns
        `self.tzinfo.tzname(self)`, raises an exception if the latter doesn’t return:py:obj:`None`or a string object.

        :rtype: str
        """
        return self.tzname() or ''

    def dayofyear(self):
        """
        Return the day of year (1-[365, 366]).

        :rtype: int
        """
        return (self.date() - Shahi.ShahiDate(self.year, 1, 1)).days + 1

    def __unicode__(self):
        """
        Return the default :py:class:`Shahi.ShahiDatetime` representation.

        .. testsetup:: api-datetime-__unicode__

            from __future__ import print_function
            from Shahi import ShahiDatetime, TehranTimezone

        .. doctest:: api-datetime-__unicode__

            >>> print(ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999, tzinfo=TehranTimezone).__unicode__())
            Shahi.ShahiDatetime(1394, 3, 24, 10, 2, 3, 999999, tzinfo=+03:30 dst:60, Yekshanbeh)

        """
        return 'Shahi.ShahiDatetime(%s, %s, %s, %s, %s, %s, %s%s, %s)' % (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            ', tzinfo=%s' % self.tzinfo.__unicode__() if self.tzinfo else '',
            self.weekdaynameascii()
        )

    __repr__ = force_encoded_string_output(__unicode__)

    def __str__(self):
        """
        The same as :py:meth:`Shahi.ShahiDatetime.isoformat(sep=' ')`.

        :rtype: str
        """
        return self.isoformat(sep=' ')

    def __add__(self, x):
        if isinstance(x, timedelta):
            return ShahiDatetime(x + self.todatetime())

        raise TypeError('ShahiDatetime object can added by timedelta or ShahiDate object')

    def __sub__(self, x):
        if isinstance(x, timedelta):
            return ShahiDatetime(self.todatetime() - x)
        elif isinstance(x, ShahiDatetime):
            return self.todatetime() - x.todatetime()
        elif isinstance(x, Shahi.ShahiDate):
            return self.todatetime() - ShahiDatetime(x).todatetime()

        raise TypeError('ShahiDatetime object can added by timedelta, ShahiDatetime or ShahiDate object')

    def __lt__(self, x):
        self._ensure_Shahi_datetime(x)
        return self.todatetime() < x.todatetime()

    def __le__(self, x):
        self._ensure_Shahi_datetime(x)
        return self.todatetime() <= x.todatetime()

    def __hash__(self):
        return hash((
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo
        ))

    def __eq__(self, x):
        if not x:
            return False
        if isinstance(x, datetime):
            return self.todatetime().__eq__(x)
        elif isinstance(x, ShahiDatetime):
            return hash(self) == hash(x)
        else:
            raise TypeError('Comparison only allowed with ShahiDatetime and datetime.datetime objects.')

    def __gt__(self, x):
        self._ensure_Shahi_datetime(x)
        return self.todatetime() > x.todatetime()

    def __ge__(self, x):
        self._ensure_Shahi_datetime(x)
        return self.todatetime() >= x.todatetime()


# # Class attributes
ShahiDatetime.min = ShahiDatetime(*ShahiDatetime.min)
ShahiDatetime.max = ShahiDatetime(*ShahiDatetime.max)
