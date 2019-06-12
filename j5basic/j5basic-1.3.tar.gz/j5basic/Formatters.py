# -*- coding: utf-8 -*-
# Copyright 2007 St James Software

"""Classes for formatting and parsing string representations of common Python types."""

import datetime
import logging
import time
import sys
from j5basic import TimeUtils

# Formatted Types

class StrftimeFormattedTypeMixIn(object):
    """Mixin for formatting with a Strftime format string."""

    def __str__(self):
        if sys.version_info.major < 3 and isinstance(self.format_str, unicode):
            # flip through into string world and back again
            return TimeUtils.strftime(self, self.format_str.encode("UTF-8")).decode("UTF-8")
        return TimeUtils.strftime(self, self.format_str)

class StrFormattedMixIn(object):
    """Mixin for formatting with a Python % string."""

    def __str__(self):
        return self.format_str % self

class FormattedDatetime(StrftimeFormattedTypeMixIn,datetime.datetime):
    def __new__(cls,format_str,*args,**kwargs):
        self = super(FormattedDatetime,cls).__new__(cls,*args,**kwargs)
        self.format_str = format_str
        return self

    def replace(self,*args,**kwargs):
        res = super(FormattedDatetime,self).replace(*args,**kwargs)
        res.format_str = self.format_str
        return res

class FormattedDate(StrftimeFormattedTypeMixIn,datetime.date):
    def __new__(cls,format_str,*args,**kwargs):
        self = super(FormattedDate,cls).__new__(cls,*args,**kwargs)
        self.format_str = format_str
        return self

    def replace(self,*args,**kwargs):
        res = super(FormattedDate,self).replace(*args,**kwargs)
        res.format_str = self.format_str
        return res

class FormattedTime(StrftimeFormattedTypeMixIn,datetime.time):
    def __new__(cls,format_str,*args,**kwargs):
        self = super(FormattedTime,cls).__new__(cls,*args,**kwargs)
        self.format_str = format_str
        return self

class FormattedFloat(StrFormattedMixIn,float):
    def __new__(cls,format_str,*args,**kwargs):
        self = super(FormattedFloat,cls).__new__(cls,*args,**kwargs)
        self.format_str = format_str
        return self

class FormattedInt(StrFormattedMixIn,int):
    def __new__(cls,format_str,*args,**kwargs):
        self = super(FormattedInt,cls).__new__(cls,*args,**kwargs)
        self.format_str = format_str
        return self

# Formatters

class FormatterBase(object):
    """A formatter object needs to implement a format(...) method.
       A formatter need not inherit from this base class.
       """

    def format(self, value):
        """Convert a value (which may be a string, unformatted type or formatted type) into a formatted type.
           - unformatted type is the Python type the formatter is designed to format.
           - formatted type is a wrapped version of the unformatted type which produces a suitably formatted string when str(..) is called on it.
           - format(...) should return None if it cannot parse the string into a formatted type."""
        raise NotImplementedError

class FormatterStrBase(FormatterBase):
    """A formatter which uses a format_str string to describe the desired format."""

    FormattedType = None # sub-classes must set this
    UnformattedType = None # sub-classes must set this

    def __init__(self, format_str):
        """format_str is a printf-style format string for floats"""
        self.format_str = format_str

    def getformatstr(self):
        return self.format_str

    def format(self,value):
        if value is None:
            return value
        if isinstance(value, self.FormattedType):
            return value
        elif isinstance(value, self.UnformattedType):
            return self._parseUnformattedType(value)
        return self._parseString(value)

    def _parseUnformattedType(self, value):
        """Sub-classes should implement this."""
        raise NotImplementedError

    def _parseString(self,value):
        """Sub-classes should implement this."""
        raise NotImplementedError

class FloatFormatter(FormatterStrBase):
    """Formats a float for user interaction.
       format_str is a Python %-string."""

    FormattedType = FormattedFloat
    UnformattedType = float

    def _parseUnformattedType(self, value):
        return FormattedFloat(self.format_str,value)

    def _parseString(self, value):
        try:
            return FormattedFloat(self.format_str,value)
        except (TypeError,ValueError):
            return None

class IntFormatter(FormatterStrBase):
    """Formats an int for user interaction.
       format_str is a Python %-string."""

    FormattedType = FormattedInt
    UnformattedType = int

    def _parseUnformattedType(self, value):
        return FormattedInt(self.format_str,value)

    def _parseString(self, value):
        try:
            return FormattedInt(self.format_str,value)
        except (TypeError,ValueError):
            return None

class DatetimeFormatter(FormatterStrBase):
    """Formats and parses dates for user interaction.
       format_str is a strftime-style format string for dates."""

    FormattedType = FormattedDatetime
    UnformattedType = datetime.datetime

    def _parseUnformattedType(self, value):
        return FormattedDatetime(self.format_str,value.year,value.month,value.day,value.hour,value.minute,value.second,value.microsecond,value.tzinfo)

    def _parseString(self,value):
        try:
            return FormattedDatetime(self.format_str,*time.strptime(value, self.format_str)[:6])
        except (TypeError, ValueError):
            logging.debug("DatetimeFormatter failed to parse out date %r with format %s" % (value, self.format_str))
            return None

class TimeFormatter(FormatterStrBase):
    """Formats and parses times for user interaction.
       format_str is a strftime-style format string for times."""

    FormattedType = FormattedTime
    UnformattedType = datetime.time

    def _parseUnformattedType(self, value):
        return FormattedTime(self.format_str,value.hour,value.minute,value.second,value.microsecond,value.tzinfo)

    def _parseString(self,value):
        try:
            return FormattedTime(self.format_str,*time.strptime(value, self.format_str)[3:6])
        except (TypeError, ValueError):
            logging.debug("TimeFormatter failed to parse out time %r with format %s" % (value, self.format_str))
            return None

class DateFormatter(FormatterStrBase):
    """Formats and parses dates for user interaction.
       format_str is a strftime-style format string for dates."""

    FormattedType = FormattedTime
    UnformattedType = datetime.date

    def _parseUnformattedType(self, value):
        return FormattedDate(self.format_str,value.year,value.month,value.day)

    def _parseString(self,value):
        try:
            return FormattedDate(self.format_str,*time.strptime(value, self.format_str)[0:3])
        except (TypeError, ValueError):
            logging.debug("DateFormatter failed to parse out date %r with format %s" % (value, self.format_str))
            return None

class LooseDatetimeFormatter(DatetimeFormatter):
    """Formats and parse dates. Tries combinations of substrings of the format string, split on space boundaries."""

    def subparts(self,parts):
        nparts = len(parts)
        for fragparts in range(nparts,0,-1): # start with the longest parts
            for start in range(0,nparts-fragparts+1): # try pieces at the front first
                yield parts[start:start+fragparts]

    def format(self,value):
        # try be strict
        if value is None:
            return None
        result = super(LooseDatetimeFormatter,self).format(value)
        if result:
            return result

        # hang loose
        formatparts = self.format_str.split()
        for frags in self.subparts(formatparts):
            subformat = " ".join(frags)
            try:
                ret = FormattedDatetime(self.format_str, *time.strptime(value, subformat)[:6])
                ret.format_str = subformat
                return ret
            except (TypeError, ValueError):
                continue

        # even loose failed
        logging.debug("LooseDateFormatter failed to parse out date %r with format %s" % (value, self.format_str))
        return None

