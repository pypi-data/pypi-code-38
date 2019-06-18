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

class ICalendarElementVAlarm :
    def __init__( self):
        self.action = None
        self.trigger = None
        self.description = None
        self.duration = None
        self.repeat = None
        self.summary = None
        pass

class __ICalendarElementVAlarmSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ICalendarElementVAlarm()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.icalendar.api.ICalendarElementVAlarmAction import ICalendarElementVAlarmAction
        from netbluemind.icalendar.api.ICalendarElementVAlarmAction import __ICalendarElementVAlarmActionSerDer__
        actionValue = value['action']
        instance.action = __ICalendarElementVAlarmActionSerDer__().parse(actionValue)
        triggerValue = value['trigger']
        instance.trigger = serder.INT.parse(triggerValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        durationValue = value['duration']
        instance.duration = serder.INT.parse(durationValue)
        repeatValue = value['repeat']
        instance.repeat = serder.INT.parse(repeatValue)
        summaryValue = value['summary']
        instance.summary = serder.STRING.parse(summaryValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.icalendar.api.ICalendarElementVAlarmAction import ICalendarElementVAlarmAction
        from netbluemind.icalendar.api.ICalendarElementVAlarmAction import __ICalendarElementVAlarmActionSerDer__
        actionValue = value.action
        instance["action"] = __ICalendarElementVAlarmActionSerDer__().encode(actionValue)
        triggerValue = value.trigger
        instance["trigger"] = serder.INT.encode(triggerValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        durationValue = value.duration
        instance["duration"] = serder.INT.encode(durationValue)
        repeatValue = value.repeat
        instance["repeat"] = serder.INT.encode(repeatValue)
        summaryValue = value.summary
        instance["summary"] = serder.STRING.encode(summaryValue)
        return instance

