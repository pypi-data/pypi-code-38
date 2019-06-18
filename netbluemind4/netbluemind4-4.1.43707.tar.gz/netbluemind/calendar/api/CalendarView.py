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

class CalendarView :
    def __init__( self):
        self.label = None
        self.type = None
        self.isDefault = None
        self.calendars = None
        pass

class __CalendarViewSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = CalendarView()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        labelValue = value['label']
        instance.label = serder.STRING.parse(labelValue)
        from netbluemind.calendar.api.CalendarViewCalendarViewType import CalendarViewCalendarViewType
        from netbluemind.calendar.api.CalendarViewCalendarViewType import __CalendarViewCalendarViewTypeSerDer__
        typeValue = value['type']
        instance.type = __CalendarViewCalendarViewTypeSerDer__().parse(typeValue)
        isDefaultValue = value['isDefault']
        instance.isDefault = serder.BOOLEAN.parse(isDefaultValue)
        calendarsValue = value['calendars']
        instance.calendars = serder.ListSerDer(serder.STRING).parse(calendarsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        labelValue = value.label
        instance["label"] = serder.STRING.encode(labelValue)
        from netbluemind.calendar.api.CalendarViewCalendarViewType import CalendarViewCalendarViewType
        from netbluemind.calendar.api.CalendarViewCalendarViewType import __CalendarViewCalendarViewTypeSerDer__
        typeValue = value.type
        instance["type"] = __CalendarViewCalendarViewTypeSerDer__().encode(typeValue)
        isDefaultValue = value.isDefault
        instance["isDefault"] = serder.BOOLEAN.encode(isDefaultValue)
        calendarsValue = value.calendars
        instance["calendars"] = serder.ListSerDer(serder.STRING).encode(calendarsValue)
        return instance

