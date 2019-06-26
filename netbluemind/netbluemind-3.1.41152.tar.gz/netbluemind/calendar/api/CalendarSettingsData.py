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

class CalendarSettingsData :
    def __init__( self):
        self.workingDays = None
        self.dayStart = None
        self.dayEnd = None
        self.minDuration = None
        self.timezoneId = None
        pass

class __CalendarSettingsDataSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = CalendarSettingsData()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.calendar.api.CalendarSettingsDataDay import CalendarSettingsDataDay
        from netbluemind.calendar.api.CalendarSettingsDataDay import __CalendarSettingsDataDaySerDer__
        workingDaysValue = value['workingDays']
        instance.workingDays = serder.ListSerDer(__CalendarSettingsDataDaySerDer__()).parse(workingDaysValue)
        dayStartValue = value['dayStart']
        instance.dayStart = serder.INT.parse(dayStartValue)
        dayEndValue = value['dayEnd']
        instance.dayEnd = serder.INT.parse(dayEndValue)
        minDurationValue = value['minDuration']
        instance.minDuration = serder.INT.parse(minDurationValue)
        timezoneIdValue = value['timezoneId']
        instance.timezoneId = serder.STRING.parse(timezoneIdValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.calendar.api.CalendarSettingsDataDay import CalendarSettingsDataDay
        from netbluemind.calendar.api.CalendarSettingsDataDay import __CalendarSettingsDataDaySerDer__
        workingDaysValue = value.workingDays
        instance["workingDays"] = serder.ListSerDer(__CalendarSettingsDataDaySerDer__()).encode(workingDaysValue)
        dayStartValue = value.dayStart
        instance["dayStart"] = serder.INT.encode(dayStartValue)
        dayEndValue = value.dayEnd
        instance["dayEnd"] = serder.INT.encode(dayEndValue)
        minDurationValue = value.minDuration
        instance["minDuration"] = serder.INT.encode(minDurationValue)
        timezoneIdValue = value.timezoneId
        instance["timezoneId"] = serder.STRING.encode(timezoneIdValue)
        return instance

