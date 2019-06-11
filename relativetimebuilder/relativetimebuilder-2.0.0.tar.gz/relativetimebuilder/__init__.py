# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import math
import dateutil.relativedelta

from aniso8601.builders.python import PythonTimeBuilder, MICROSECONDS_PER_SECOND, MICROSECONDS_PER_MINUTE, MICROSECONDS_PER_HOUR, MICROSECONDS_PER_DAY, MICROSECONDS_PER_WEEK, MICROSECONDS_PER_MONTH, MICROSECONDS_PER_YEAR

class RelativeValueError(ValueError):
    """Raised when an invalid value is given for calendar level accuracy."""

class RelativeTimeBuilder(PythonTimeBuilder):
    @classmethod
    def build_duration(cls, PnY=None, PnM=None, PnW=None, PnD=None, TnH=None,
                       TnM=None, TnS=None):
        if ((PnY is not None and '.' in PnY)
                or (PnM is not None and '.' in PnM)):
            #https://github.com/dateutil/dateutil/issues/40
            raise RelativeValueError('Fractional months and years are not '
                                     'defined for relative durations.')

        years = 0
        months = 0
        days = 0
        weeks = 0
        hours = 0
        minutes = 0
        seconds = 0
        microseconds = 0

        if PnY is not None:
            years = cls.cast(PnY, int,
                             thrownmessage='Invalid year string.')

        if PnM is not None:
            months = cls.cast(PnM, int,
                              thrownmessage='Invalid month string.')

        if PnW is not None:
            if '.' in PnW:
                weeks, remainingmicroseconds = cls._split_to_microseconds(PnW, MICROSECONDS_PER_WEEK, 'Invalid week string.')
                microseconds += remainingmicroseconds
            else:
                weeks = cls.cast(PnW, int,
                                 thrownmessage='Invalid week string.')

        if PnD is not None:
            if '.' in PnD:
                days, remainingmicroseconds = cls._split_to_microseconds(PnD, MICROSECONDS_PER_DAY, 'Invalid day string.')
                microseconds += remainingmicroseconds
            else:
                days = cls.cast(PnD, int,
                                thrownmessage='Invalid day string.')

        if TnH is not None:
            if '.' in TnH:
                hours, remainingmicroseconds = cls._split_to_microseconds(TnH, MICROSECONDS_PER_HOUR, 'Invalid hour string.')
                microseconds += remainingmicroseconds
            else:
                hours = cls.cast(TnH, int,
                                 thrownmessage='Invalid hour string.')

        if TnM is not None:
            if '.' in TnM:
                minutes, remainingmicroseconds = cls._split_to_microseconds(TnM, MICROSECONDS_PER_MINUTE, 'Invalid minute string.')
                microseconds += remainingmicroseconds
            else:
                minutes = cls.cast(TnM, int,
                                   thrownmessage='Invalid minute string.')

        if TnS is not None:
            if '.' in TnS:
                seconds, remainingmicroseconds = cls._split_to_microseconds(TnS, MICROSECONDS_PER_SECOND, 'Invalid second string.')
                microseconds += remainingmicroseconds
            else:
                seconds = cls.cast(TnS, int,
                                   thrownmessage='Invalid second string.')

        years, months, weeks, days, hours, minutes, seconds, microseconds = PythonTimeBuilder._distribute_microseconds(microseconds, (years, months, weeks, days, hours, minutes, seconds), (MICROSECONDS_PER_YEAR, MICROSECONDS_PER_MONTH, MICROSECONDS_PER_WEEK, MICROSECONDS_PER_DAY, MICROSECONDS_PER_HOUR, MICROSECONDS_PER_MINUTE, MICROSECONDS_PER_SECOND))

        return dateutil.relativedelta.relativedelta(years=years,
                                                    months=months,
                                                    weeks=weeks,
                                                    days=days,
                                                    hours=hours,
                                                    minutes=minutes,
                                                    seconds=seconds,
                                                    microseconds=microseconds)

    @staticmethod
    def _expand(f):
        #Expands a float into a decimal string
        #Based on _truncate from the PythonTimeBuilder
        floatstr = repr(f)

        if 'e' in floatstr or 'E' in floatstr:
            #Expand the exponent notation
            eindex = -1

            if 'e' in floatstr:
                eindex = floatstr.index('e')
            else:
                eindex = floatstr.index('E')

            exponent = int(floatstr[eindex + 1:])

            if exponent >= 0:
                return '{0:.{1}f}'.format(f, 0)
            else:
                #2 is a fudge factor to prevent rounding
                return '{0:.{1}f}'.format(f, abs(exponent) + 2)

        return floatstr
