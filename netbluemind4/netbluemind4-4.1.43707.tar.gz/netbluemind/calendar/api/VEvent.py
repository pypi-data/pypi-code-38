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
class VEvent (ICalendarElement):
    def __init__( self):
        ICalendarElement.__init__(self)
        self.dtend = None
        self.transparency = None
        pass

class __VEventSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VEvent()
        __ICalendarElementSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtendValue = value['dtend']
        instance.dtend = __BmDateTimeSerDer__().parse(dtendValue)
        from netbluemind.calendar.api.VEventTransparency import VEventTransparency
        from netbluemind.calendar.api.VEventTransparency import __VEventTransparencySerDer__
        transparencyValue = value['transparency']
        instance.transparency = __VEventTransparencySerDer__().parse(transparencyValue)
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
        dtendValue = value.dtend
        instance["dtend"] = __BmDateTimeSerDer__().encode(dtendValue)
        from netbluemind.calendar.api.VEventTransparency import VEventTransparency
        from netbluemind.calendar.api.VEventTransparency import __VEventTransparencySerDer__
        transparencyValue = value.transparency
        instance["transparency"] = __VEventTransparencySerDer__().encode(transparencyValue)
        return instance

