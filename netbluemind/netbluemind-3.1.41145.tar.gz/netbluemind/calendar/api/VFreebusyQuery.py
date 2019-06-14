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

class VFreebusyQuery :
    def __init__( self):
        self.dtstart = None
        self.dtend = None
        self.excludedEvents = None
        pass

class __VFreebusyQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VFreebusyQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtstartValue = value['dtstart']
        instance.dtstart = __BmDateTimeSerDer__().parse(dtstartValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtendValue = value['dtend']
        instance.dtend = __BmDateTimeSerDer__().parse(dtendValue)
        excludedEventsValue = value['excludedEvents']
        instance.excludedEvents = serder.ListSerDer(serder.STRING).parse(excludedEventsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtstartValue = value.dtstart
        instance["dtstart"] = __BmDateTimeSerDer__().encode(dtstartValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        dtendValue = value.dtend
        instance["dtend"] = __BmDateTimeSerDer__().encode(dtendValue)
        excludedEventsValue = value.excludedEvents
        instance["excludedEvents"] = serder.ListSerDer(serder.STRING).encode(excludedEventsValue)
        return instance

