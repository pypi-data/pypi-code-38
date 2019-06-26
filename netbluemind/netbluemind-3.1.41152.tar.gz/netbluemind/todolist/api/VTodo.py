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

from netbluemind.icalendar.api.ICalendarElement import ICalendarElement
from netbluemind.icalendar.api.ICalendarElement import __ICalendarElementSerDer__
class VTodo (ICalendarElement):
    def __init__( self):
        ICalendarElement.__init__(self)
        self.due = None
        self.percent = None
        self.completed = None
        self.uid = None
        pass

class __VTodoSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VTodo()
        __ICalendarElementSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dueValue = value['due']
        instance.due = __BmDateTimeSerDer__().parse(dueValue)
        percentValue = value['percent']
        instance.percent = serder.INT.parse(percentValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        completedValue = value['completed']
        instance.completed = __BmDateTimeSerDer__().parse(completedValue)
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __ICalendarElementSerDer__().encodeInternal(value,instance)

        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dueValue = value.due
        instance["due"] = __BmDateTimeSerDer__().encode(dueValue)
        percentValue = value.percent
        instance["percent"] = serder.INT.encode(percentValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        completedValue = value.completed
        instance["completed"] = __BmDateTimeSerDer__().encode(completedValue)
        uidValue = value.uid
        instance["uid"] = serder.STRING.encode(uidValue)
        return instance

