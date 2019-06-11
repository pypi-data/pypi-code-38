# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import operator

import numpy as np

from decimal import Decimal
from aniso8601.builders import BaseTimeBuilder, TupleBuilder
from aniso8601.builders.python import PythonTimeBuilder
from aniso8601.exceptions import (HoursOutOfBoundsError, LeapSecondError,
                                  MidnightBoundsError, MinutesOutOfBoundsError,
                                  SecondsOutOfBoundsError)
from numpytimebuilder.constants import (DAYS_PER_MONTH, DAYS_PER_WEEK,
                                        DAYS_PER_YEAR)
from numpytimebuilder.util import apply_duration, decompose

class NumPyTimeBuilder(BaseTimeBuilder):
    @classmethod
    def build_date(cls, YYYY=None, MM=None, DD=None, Www=None, D=None,
                   DDD=None):
        return np.datetime64(PythonTimeBuilder.build_date(YYYY=YYYY, MM=MM,
                                                          DD=DD, Www=Www,
                                                          D=D, DDD=DDD))

    @classmethod
    def build_time(cls, hh=None, mm=None, ss=None, tz=None):
        raise NotImplementedError('No compatible numpy time64 type.')

    @classmethod
    def build_datetime(cls, date, time):
        if time[3] is not None:
            raise NotImplementedError('Timezones are not supported by numpy '
                                      'datetime64 type.')

        date = cls.build_date(YYYY=date[0], MM=date[1], DD=date[2],
                              Www=date[3], D=date[4], DDD=date[5])

        if time[0] is not None:
            hourstr = time[0].rjust(2, '0')
        else:
            hourstr = '00'

        if time[1] is not None:
            minutestr = time[1].rjust(2, '0')
        else:
            minutestr = '00'

        if time[2] is not None:
            secondstr = time[2].rjust(2, '0')

            if '.' in secondstr:
                #Truncate to attosecond
                secondstr = secondstr[0:secondstr.index('.') + 19]
        else:
            secondstr = '00'

        #TODO: Add range checks for supported numpy spans
        #https://docs.scipy.org/doc/numpy/reference/arrays.datetime.html#datetime-units
        #https://github.com/numpy/numpy/pull/11873
        #https://github.com/numpy/numpy/issues/8161
        #https://github.com/numpy/numpy/issues/5452
        try:
            return np.datetime64(str(date)
                                 + 'T'
                                 + hourstr + ':' + minutestr + ':' + secondstr)
        except ValueError as e:
            #Range checks
            hours = 0
            minutes = 0
            seconds = 0

            floathours = float(0)
            floatminutes = float(0)
            floatseconds = float(0)

            if '.' in hourstr:
                floathours = BaseTimeBuilder.cast(hourstr,
                                                  float,
                                                  thrownmessage=
                                                  'Invalid hour string.')
                hours = 0
            else:
                hours = BaseTimeBuilder.cast(hourstr,
                                             int,
                                             thrownmessage=
                                             'Invalid hour string.')

            if '.' in minutestr:
                floatminutes = BaseTimeBuilder.cast(minutestr,
                                                    float,
                                                    thrownmessage=
                                                    'Invalid minute string.')
                minutes = 0
            else:
                minutes = BaseTimeBuilder.cast(minutestr,
                                               int,
                                               thrownmessage=
                                               'Invalid minute string.')

            if '.' in secondstr:
                floatseconds = BaseTimeBuilder.cast(secondstr,
                                                    float,
                                                    thrownmessage=
                                                    'Invalid second string.')
                seconds = 0
            else:
                seconds = BaseTimeBuilder.cast(secondstr,
                                               int,
                                               thrownmessage=
                                               'Invalid second string.')

            if (hours == 23 and floathours == 0
                    and minutes == 59 and floatminutes == 0
                    and seconds == 60 and floatseconds == 0):
                raise LeapSecondError('Leap seconds are not supported.')

            if (hours == 24 and floathours == 0
                    and (minutes != 0 or floatminutes != 0
                         or seconds != 0 or floatseconds != 0)):
                raise MidnightBoundsError('Hour 24 may only represent '
                                          'midnight.')

            if hours > 24 or floathours > 24:
                raise HoursOutOfBoundsError('Hour must be between 0..24 with '
                                            '24 representing midnight.')

            if minutes >= 60 or floatminutes >= 60:
                raise MinutesOutOfBoundsError('Minutes must be less than 60.')

            if seconds >= 60 or floatseconds >= 60:
                raise SecondsOutOfBoundsError('Seconds must be less than 60.')

            #Unknown exception
            raise e

    @classmethod
    def build_duration(cls, PnY=None, PnM=None, PnW=None, PnD=None, TnH=None,
                       TnM=None, TnS=None):
        #Build a delta for every numpy timedelta64 type
        years = Decimal(0)
        months = Decimal(0)
        days = Decimal(0)
        weeks = Decimal(0)
        hours = Decimal(0)
        minutes = Decimal(0)
        seconds = Decimal(0)

        if PnY is not None:
            years = cls.cast(PnY, Decimal,
                             thrownmessage='Invalid year string.')

        if PnM is not None:
            months = cls.cast(PnM, Decimal,
                              thrownmessage='Invalid month string.')

        if PnD is not None:
            days = cls.cast(PnD, Decimal,
                            thrownmessage='Invalid day string.')

        if PnW is not None:
            weeks = cls.cast(PnW, Decimal,
                             thrownmessage='Invalid week string.')

        if TnH is not None:
            hours = cls.cast(TnH, Decimal,
                             thrownmessage='Invalid hour string.')

        if TnM is not None:
            minutes = cls.cast(TnM, Decimal,
                               thrownmessage='Invalid minute string.')

        if TnS is not None:
            seconds = cls.cast(TnS, Decimal,
                               thrownmessage='Invalid second string.')

        #Convert years and months to days since numpy won't apply
        #year or month deltas to datetimes with day resolution
        days += years * DAYS_PER_YEAR
        days += months * DAYS_PER_MONTH

        #Convert weeks to days to save an argument
        days += weeks * DAYS_PER_WEEK

        return decompose(days, hours, minutes, seconds)

    @classmethod
    def build_interval(cls, start=None, end=None, duration=None):
        if start is not None and end is not None:
            #<start>/<end>
            startobject = cls._build_object(start)
            endobject = cls._build_object(end)

            return (startobject, endobject)

        durationobject = cls._build_object(duration)

        #Determine if datetime promotion is required, forced to boolean
        #because numpy comparisons result in 1d arrays
        datetimerequired = bool(duration[4] is not None
                                or duration[5] is not None
                                or duration[6] is not None
                                or durationobject[1] != np.timedelta64(0)
                                or durationobject[2] != np.timedelta64(0)
                                or durationobject[3] != np.timedelta64(0)
                                or durationobject[4] != np.timedelta64(0)
                                or durationobject[5] != np.timedelta64(0)
                                or durationobject[6] != np.timedelta64(0)
                                or durationobject[7] != np.timedelta64(0)
                                or durationobject[8] != np.timedelta64(0)
                                or durationobject[9] != np.timedelta64(0))

        if end is not None:
            #<duration>/<end>
            endobject = cls._build_object(end)

            if end[-1] == 'date' and datetimerequired is True:
                #<end> is a date, and <duration> requires datetime resolution
                nulltime = TupleBuilder.build_time() #Time for elapsed datetime

                return (endobject,
                        apply_duration(cls.build_datetime(end, nulltime),
                                       durationobject, operator.sub))

            return (endobject,
                    apply_duration(endobject,
                                   durationobject, operator.sub))

        #<start>/<duration>
        startobject = cls._build_object(start)

        if start[-1] == 'date' and datetimerequired is True:
            #<start> is a date, and <duration> requires datetime resolution
            nulltime = TupleBuilder.build_time() #Time for elapsed datetime

            return (startobject,
                    apply_duration(cls.build_datetime(start, nulltime),
                                   durationobject, operator.add))

        return (startobject,
                apply_duration(startobject,
                               durationobject, operator.add))

    @classmethod
    def build_repeating_interval(cls, R=None, Rnn=None, interval=None):
        startobject = None
        endobject = None

        if interval[0] is not None:
            startobject = cls._build_object(interval[0])

        if interval[1] is not None:
            endobject = cls._build_object(interval[1])

        if interval[2] is not None:
            durationobject = cls._build_object(interval[2])
        else:
            #Generator builders use apply_duration internally, which requires
            #a tuple of timedelta64 objects
            durationobject = ((endobject - startobject),)

        if R is True:
            if startobject is not None:
                return cls._date_generator_unbounded(startobject,
                                                     durationobject,
                                                     operator.add)

            return cls._date_generator_unbounded(endobject,
                                                 durationobject,
                                                 operator.sub)

        iterations = BaseTimeBuilder.cast(Rnn, int,
                                          thrownmessage='Invalid iterations.')

        if startobject is not None:
            return cls._date_generator(startobject, durationobject,
                                       iterations, operator.add)

        return cls._date_generator(endobject, durationobject,
                                   iterations, operator.sub)

    @classmethod
    def build_timezone(cls, negative=None, Z=None, hh=None, mm=None, name=''):
        raise NotImplementedError('Timezones are not supported by '
                                  'numpy datetime64 type.')

    @staticmethod
    def _date_generator(startdate, duration, iterations, op):
        currentdate = startdate
        currentiteration = 0

        while currentiteration < iterations:
            yield currentdate

            #Update the values
            currentdate = apply_duration(currentdate, duration, op)
            currentiteration += 1

    @staticmethod
    def _date_generator_unbounded(startdate, duration, op):
        currentdate = startdate

        while True:
            yield currentdate

            #Update the value
            currentdate = apply_duration(currentdate, duration, op)
