class WeekdayMap(object):
    """A utility Class which maps days of week to a numeric value. Used for scheduling.

    Usage:
        >>> WeekdayMap.weekdays_from_value(7)
        ['Thursday', 'Friday', 'Saturday']

        >>> WeekdayMap.DAYS
        {
            64: 'Sunday',
            32: 'Monday',
            16: 'Tuesday',
            8:  'Wednesday',
            4:  'Thursday',
            2:  'Friday',
            1:  'Saturday',
        }
    """

    DAYS = {
        64: 'Sunday',
        32: 'Monday',
        16: 'Tuesday',
        8:  'Wednesday',
        4:  'Thursday',
        2:  'Friday',
        1:  'Saturday',
    }

    @classmethod
    def weekdays_from_value(cls, val, truncate=False):
        """Get list of weekday names that are valid for particular run value.

        args:
          - VALUE (int) 0-127
          - TRUNCATE (bool|default=False) limit names to only first two chars

        returns:
            a list
        """
        if val < 0 or val > 127:
            raise ValueError("Value must be from 0 to 127")

        results = []
        for n in sorted(cls.DAYS.keys(), reverse=True):
            if (val & n):
                dow = cls.DAYS[n]
                if truncate:
                    results.append("".join(list(dow)[0:2]))
                else:
                    results.append(dow)

        return results
