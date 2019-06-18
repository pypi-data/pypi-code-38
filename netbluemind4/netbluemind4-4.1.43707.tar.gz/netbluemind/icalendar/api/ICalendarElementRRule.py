#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder

class ICalendarElementRRule :
    def __init__( self):
        self.frequency = None
        self.count = None
        self.until = None
        self.interval = None
        self.bySecond = None
        self.byMinute = None
        self.byHour = None
        self.byDay = None
        self.byMonthDay = None
        self.byYearDay = None
        self.byWeekNo = None
        self.byMonth = None
        pass

class __ICalendarElementRRuleSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ICalendarElementRRule()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.icalendar.api.ICalendarElementRRuleFrequency import ICalendarElementRRuleFrequency
        from netbluemind.icalendar.api.ICalendarElementRRuleFrequency import __ICalendarElementRRuleFrequencySerDer__
        frequencyValue = value['frequency']
        instance.frequency = __ICalendarElementRRuleFrequencySerDer__().parse(frequencyValue)
        countValue = value['count']
        instance.count = serder.INT.parse(countValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        untilValue = value['until']
        instance.until = __BmDateTimeSerDer__().parse(untilValue)
        intervalValue = value['interval']
        instance.interval = serder.INT.parse(intervalValue)
        bySecondValue = value['bySecond']
        instance.bySecond = serder.ListSerDer(serder.INT).parse(bySecondValue)
        byMinuteValue = value['byMinute']
        instance.byMinute = serder.ListSerDer(serder.INT).parse(byMinuteValue)
        byHourValue = value['byHour']
        instance.byHour = serder.ListSerDer(serder.INT).parse(byHourValue)
        from netbluemind.icalendar.api.ICalendarElementRRuleWeekDay import ICalendarElementRRuleWeekDay
        from netbluemind.icalendar.api.ICalendarElementRRuleWeekDay import __ICalendarElementRRuleWeekDaySerDer__
        byDayValue = value['byDay']
        instance.byDay = serder.ListSerDer(__ICalendarElementRRuleWeekDaySerDer__()).parse(byDayValue)
        byMonthDayValue = value['byMonthDay']
        instance.byMonthDay = serder.ListSerDer(serder.INT).parse(byMonthDayValue)
        byYearDayValue = value['byYearDay']
        instance.byYearDay = serder.ListSerDer(serder.INT).parse(byYearDayValue)
        byWeekNoValue = value['byWeekNo']
        instance.byWeekNo = serder.ListSerDer(serder.INT).parse(byWeekNoValue)
        byMonthValue = value['byMonth']
        instance.byMonth = serder.ListSerDer(serder.INT).parse(byMonthValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.icalendar.api.ICalendarElementRRuleFrequency import ICalendarElementRRuleFrequency
        from netbluemind.icalendar.api.ICalendarElementRRuleFrequency import __ICalendarElementRRuleFrequencySerDer__
        frequencyValue = value.frequency
        instance["frequency"] = __ICalendarElementRRuleFrequencySerDer__().encode(frequencyValue)
        countValue = value.count
        instance["count"] = serder.INT.encode(countValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        untilValue = value.until
        instance["until"] = __BmDateTimeSerDer__().encode(untilValue)
        intervalValue = value.interval
        instance["interval"] = serder.INT.encode(intervalValue)
        bySecondValue = value.bySecond
        instance["bySecond"] = serder.ListSerDer(serder.INT).encode(bySecondValue)
        byMinuteValue = value.byMinute
        instance["byMinute"] = serder.ListSerDer(serder.INT).encode(byMinuteValue)
        byHourValue = value.byHour
        instance["byHour"] = serder.ListSerDer(serder.INT).encode(byHourValue)
        from netbluemind.icalendar.api.ICalendarElementRRuleWeekDay import ICalendarElementRRuleWeekDay
        from netbluemind.icalendar.api.ICalendarElementRRuleWeekDay import __ICalendarElementRRuleWeekDaySerDer__
        byDayValue = value.byDay
        instance["byDay"] = serder.ListSerDer(__ICalendarElementRRuleWeekDaySerDer__()).encode(byDayValue)
        byMonthDayValue = value.byMonthDay
        instance["byMonthDay"] = serder.ListSerDer(serder.INT).encode(byMonthDayValue)
        byYearDayValue = value.byYearDay
        instance["byYearDay"] = serder.ListSerDer(serder.INT).encode(byYearDayValue)
        byWeekNoValue = value.byWeekNo
        instance["byWeekNo"] = serder.ListSerDer(serder.INT).encode(byWeekNoValue)
        byMonthValue = value.byMonth
        instance["byMonth"] = serder.ListSerDer(serder.INT).encode(byMonthValue)
        return instance

