# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import numpy as np

from decimal import getcontext
from numpytimebuilder import compat
from numpytimebuilder.constants import (ATTOSECONDS_PER_FEMTOSECOND,
                                        FEMTOSECONDS_PER_PICOSECOND,
                                        HOURS_PER_DAY,
                                        MICROSECONDS_PER_MILLISECOND,
                                        MILLISECONDS_PER_SECOND,
                                        MINUTES_PER_HOUR,
                                        NANOSECONDS_PER_MICROSECOND,
                                        PICOSECONDS_PER_NANOSECOND,
                                        SECONDS_PER_MINUTE)

def decompose(days, hours, minutes, seconds, components=None):
    #Recursively build a delta for every type, keeping track of remainders
    if components is None:
        components = [None, None, None, None, None,
                      None, None, None, None, None]

    if compat.long(days) == days:
        if components[0] is None:
            components[0] = np.timedelta64(compat.long(days), 'D')
    else:
        integerdays, fractionaldays = decimal_split(days)

        #Move the fraction to hours
        decompose(integerdays, hours + fractionaldays * HOURS_PER_DAY,
                  minutes, seconds,
                  components)

    if compat.long(hours) == hours:
        if components[1] is None:
            components[1] = np.timedelta64(compat.long(hours), 'h')
    else:
        integerhours, fractionalhours = decimal_split(hours)

        #Move the fraction to minutes
        decompose(days, integerhours,
                  minutes + fractionalhours * MINUTES_PER_HOUR, seconds,
                  components)

    if compat.long(minutes) == minutes:
        if components[2] is None:
            components[2] = np.timedelta64(compat.long(minutes), 'm')
    else:
        integerminutes, fractionalminutes = decimal_split(minutes)

        #Move the fraction to seconds
        decompose(days, hours,
                  integerminutes,
                  seconds + fractionalminutes * SECONDS_PER_MINUTE,
                  components)

    if components[3] is None:
        if compat.long(seconds) == seconds:
            components[3] = np.timedelta64(compat.long(seconds), 's')
            components[4] = np.timedelta64(0, 'ms')
            components[5] = np.timedelta64(0, 'us')
            components[6] = np.timedelta64(0, 'ns')
            components[7] = np.timedelta64(0, 'ps')
            components[8] = np.timedelta64(0, 'fs')
            components[9] = np.timedelta64(0, 'as')
        else:
            integerseconds, fractionalseconds = decimal_split(seconds)

            components[3] = np.timedelta64(compat.long(integerseconds), 's')

            #Calculate milliseconds
            integerms, fractionalms = decimal_split(fractionalseconds
                                                    * MILLISECONDS_PER_SECOND)

            components[4] = np.timedelta64(compat.long(integerms), 'ms')

            #Calculate microseconds
            integerus, fractionalus = decimal_split(fractionalms
                                                    * MICROSECONDS_PER_MILLISECOND)

            components[5] = np.timedelta64(compat.long(integerus), 'us')

            #Calculate nanoseconds
            integerns, fractionalns = decimal_split(fractionalus
                                                    * NANOSECONDS_PER_MICROSECOND)

            components[6] = np.timedelta64(compat.long(integerns), 'ns')

            #Calculate picoseconds
            integerps, fractionalps = decimal_split(fractionalns
                                                    * PICOSECONDS_PER_NANOSECOND)

            components[7] = np.timedelta64(compat.long(integerps), 'ps')

            #Calculate femtoseconds
            integerfs, fractionalfs = decimal_split(fractionalps
                                                    * FEMTOSECONDS_PER_PICOSECOND)

            components[8] = np.timedelta64(compat.long(integerfs), 'fs')

            #Calculate attoseconds, losing any remaining precision
            components[9] = np.timedelta64(compat.long(fractionalfs
                                                       * ATTOSECONDS_PER_FEMTOSECOND),
                                           'as')

    return tuple(components)

def apply_duration(target, duration, operator):
    #Given an np.datetime64 target, a tuple of np.timedelta64 serving as
    #the duration, and a Python operator function, return a new datetime64
    #with the given duration applied
    datecomponents = ['years', 'months', 'weeks', 'days']

    result = target

    #We ignore hours, minutes, seconds, etc for dates
    usetimeresolution = 'T' in str(target)

    for component in duration:
        #Only apply relevant components
        if (usetimeresolution is True
                or str(component).split(None, 1)[-1] in datecomponents):
            #Don't apply 0s to minimize any rounding errors
            if component != np.timedelta64(0):
                result = operator(result, component)

    return result

def decimal_split(decimal):
    #Splits a Decimal object into integer and fractional parts, returned as Decimal
    integerpart, fractionalpart = getcontext().divmod(decimal, 1)

    return (integerpart, fractionalpart)
