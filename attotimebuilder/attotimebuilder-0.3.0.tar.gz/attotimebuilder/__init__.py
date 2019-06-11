# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import datetime
import attotime

from decimal import Decimal
from aniso8601.builders import BaseTimeBuilder, TupleBuilder
from aniso8601.builders.python import PythonTimeBuilder
from aniso8601.exceptions import (HoursOutOfBoundsError, LeapSecondError,
                                  MidnightBoundsError, MinutesOutOfBoundsError,
                                  SecondsOutOfBoundsError)

class AttoTimeBuilder(PythonTimeBuilder):
    @classmethod
    def build_time(cls, hh=None, mm=None, ss=None, tz=None):
        #Builds a time from the given parts, handling fractional arguments
        #where necessary
        hours = 0
        minutes = 0
        seconds = 0

        decimalhours = Decimal(0)
        decimalminutes = Decimal(0)
        decimalseconds = Decimal(0)

        if hh is not None:
            if '.' in hh:
                decimalhours = BaseTimeBuilder.cast(hh,
                                                  Decimal,
                                                  thrownmessage=
                                                  'Invalid hour string.')
                hours = 0
            else:
                hours = BaseTimeBuilder.cast(hh,
                                             int,
                                             thrownmessage=
                                             'Invalid hour string.')

        if mm is not None:
            if '.' in mm:
                decimalminutes = BaseTimeBuilder.cast(mm,
                                                    Decimal,
                                                    thrownmessage=
                                                    'Invalid minute string.')
                minutes = 0
            else:
                minutes = BaseTimeBuilder.cast(mm,
                                               int,
                                               thrownmessage=
                                               'Invalid minute string.')

        if ss is not None:
            if '.' in ss:
                decimalseconds = BaseTimeBuilder.cast(ss,
                                                      Decimal,
                                                      thrownmessage=
                                                      'Invalid second string.')
                seconds = 0
            else:
                seconds = BaseTimeBuilder.cast(ss,
                                               int,
                                               thrownmessage=
                                               'Invalid second string.')

        #Range checks
        if (hours == 23 and decimalhours == 0 and minutes == 59
                and decimalminutes == 0 and seconds == 60
                and decimalseconds == 0):
            raise LeapSecondError('Leap seconds are not supported.')

        if (hours == 24
                and (minutes != 0 or decimalminutes != 0 or seconds != 0
                     or decimalseconds != 0)) or 24 < decimalhours < 25:
            raise MidnightBoundsError('Hour 24 may only represent midnight.')

        if hours > 24 or decimalhours > 24:
            raise HoursOutOfBoundsError('Hour must be between 0..24 with '
                                        '24 representing midnight.')

        if minutes >= 60 or decimalminutes >= 60:
            raise MinutesOutOfBoundsError('Minutes must be less than 60.')

        if seconds >= 60 or decimalseconds >= 60:
            raise SecondsOutOfBoundsError('Seconds must be less than 60.')

        #Fix ranges that have passed range checks
        if hours == 24:
            hours = 0
            minutes = 0
            seconds = 0

        #Datetimes don't handle fractional components, so we use a timedelta
        if tz is not None:
            return (attotime.attodatetime(1, 1, 1,
                                          hour=hours,
                                          minute=minutes,
                                          second=seconds,
                                          tzinfo=cls._build_object(tz))
                    + attotime.attotimedelta(hours=decimalhours,
                                             minutes=decimalminutes,
                                             seconds=decimalseconds)
                   ).timetz()

        return (attotime.attodatetime(1, 1, 1,
                                      hour=hours,
                                      minute=minutes,
                                      second=seconds)
                + attotime.attotimedelta(hours=decimalhours,
                                         minutes=decimalminutes,
                                         seconds=decimalseconds)
               ).time()

    @classmethod
    def build_datetime(cls, date, time):
        return attotime.attodatetime.combine(cls._build_object(date),
                                             cls._build_object(time))

    @classmethod
    def build_duration(cls, PnY=None, PnM=None, PnW=None, PnD=None, TnH=None,
                       TnM=None, TnS=None):
        years = 0
        months = 0
        days = 0
        weeks = 0
        hours = 0
        minutes = 0
        seconds = 0

        if PnY is not None:
            years = BaseTimeBuilder.cast(PnY,
                                         Decimal,
                                         thrownmessage=
                                         'Invalid year string.')

        if PnM is not None:
            months = BaseTimeBuilder.cast(PnM,
                                          Decimal,
                                          thrownmessage=
                                          'Invalid month string.')
        if PnD is not None:
            days = BaseTimeBuilder.cast(PnD,
                                        Decimal,
                                        thrownmessage=
                                        'Invalid day string.')

        if PnW is not None:
            if '.' in PnW:
                weeks = BaseTimeBuilder.cast(PnW,
                                             Decimal,
                                             thrownmessage=
                                             'Invalid week string.')
            else:
                weeks = BaseTimeBuilder.cast(PnW,
                                             int,
                                             thrownmessage=
                                             'Invalid week string.')

        if TnH is not None:
            if '.' in TnH:
                hours = BaseTimeBuilder.cast(TnH,
                                             Decimal,
                                             thrownmessage=
                                             'Invalid hour string.')
            else:
                hours = BaseTimeBuilder.cast(TnH,
                                             int,
                                             thrownmessage=
                                             'Invalid hour string.')

        if TnM is not None:
            if '.' in TnM:
                minutes = BaseTimeBuilder.cast(TnM,
                                               Decimal,
                                               thrownmessage=
                                               'Invalid minute string.')
            else:
                minutes = BaseTimeBuilder.cast(TnM,
                                               int,
                                               thrownmessage=
                                               'Invalid minute string.')

        if TnS is not None:
            if '.' in TnS:
                seconds = BaseTimeBuilder.cast(TnS,
                                               Decimal,
                                               thrownmessage=
                                               'Invalid second string.')
            else:
                seconds = BaseTimeBuilder.cast(TnS,
                                               int,
                                               thrownmessage=
                                               'Invalid second string.')

        #Note that weeks can be handled without conversion to days
        totaldays = years * 365 + months * 30 + days

        return attotime.attotimedelta(days=totaldays,
                                      seconds=seconds,
                                      minutes=minutes,
                                      hours=hours,
                                      weeks=weeks)

    @classmethod
    def build_interval(cls, start=None, end=None, duration=None):
        if start is not None and end is not None:
            #<start>/<end>
            startobject = cls._build_object(start)
            endobject = cls._build_object(end)

            return (startobject, endobject)

        durationobject = cls._build_object(duration)

        #Determine if datetime promotion is required
        datetimerequired = (duration[4] is not None
                            or duration[5] is not None
                            or duration[6] is not None
                            or durationobject.seconds != 0
                            or durationobject.microseconds != 0
                            or durationobject.nanoseconds != 0)

        if end is not None:
            #<duration>/<end>
            endobject = cls._build_object(end)
            if end[-1] == 'date':
                enddatetime = cls.build_datetime(end, TupleBuilder.build_time())

                if datetimerequired is True:
                    #<end> is a date, and <duration> requires datetime resolution
                    return (endobject,
                            enddatetime - durationobject)

                #<end> is a date, but attotimedeltas can only be applied
                #to attodatetimes
                return (endobject,
                        (enddatetime - durationobject).date())

            return (endobject,
                    endobject
                    - durationobject)

        #<start>/<duration>
        startobject = cls._build_object(start)

        if start[-1] == 'date':
            startdatetime = cls.build_datetime(start, TupleBuilder.build_time())

            if datetimerequired is True:
                #<start> is a date, and <duration> requires datetime resolution
                return (startobject,
                        startdatetime + durationobject)

            #<start> is a date, but attotimedeltas can only be applied
            #to attodatetimes
            return (startobject,
                    (startdatetime + durationobject).date())

        return (startobject,
                startobject
                + durationobject)

    @staticmethod
    def _date_generator(start, timedelta, iterations):
        if isinstance(start, datetime.date):
            #No attodate object compatible with attotimedelta, so convert
            #to attodatetime
            current = attotime.attodatetime(year=start.year,
                                            month=start.month,
                                            day=start.day)
            returnasdate = True
        else:
            current = start
            returnasdate = False

        currentiteration = 0

        while currentiteration < iterations:
            if returnasdate is True:
                yield current.date()
            else:
                yield current

            #Update the values
            current += timedelta
            currentiteration += 1

    @staticmethod
    def _date_generator_unbounded(start, timedelta):
        if isinstance(start, datetime.date):
            #No attodate object compatible with attotimedelta, so convert
            #to attodatetime
            current = attotime.attodatetime(year=start.year,
                                            month=start.month,
                                            day=start.day)
            returnasdate = True
        else:
            current = start
            returnasdate = False

        while True:
            if returnasdate is True:
                yield current.date()
            else:
                yield current

            #Update the value
            current += timedelta
