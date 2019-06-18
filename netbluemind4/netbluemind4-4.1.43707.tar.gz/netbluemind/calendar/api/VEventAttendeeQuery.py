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

class VEventAttendeeQuery :
    def __init__( self):
        self.dir = None
        self.calendarOwnerAsDir = None
        self.partStatus = None
        pass

class __VEventAttendeeQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VEventAttendeeQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        dirValue = value['dir']
        instance.dir = serder.STRING.parse(dirValue)
        calendarOwnerAsDirValue = value['calendarOwnerAsDir']
        instance.calendarOwnerAsDir = serder.BOOLEAN.parse(calendarOwnerAsDirValue)
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import ICalendarElementParticipationStatus
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import __ICalendarElementParticipationStatusSerDer__
        partStatusValue = value['partStatus']
        instance.partStatus = __ICalendarElementParticipationStatusSerDer__().parse(partStatusValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        dirValue = value.dir
        instance["dir"] = serder.STRING.encode(dirValue)
        calendarOwnerAsDirValue = value.calendarOwnerAsDir
        instance["calendarOwnerAsDir"] = serder.BOOLEAN.encode(calendarOwnerAsDirValue)
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import ICalendarElementParticipationStatus
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import __ICalendarElementParticipationStatusSerDer__
        partStatusValue = value.partStatus
        instance["partStatus"] = __ICalendarElementParticipationStatusSerDer__().encode(partStatusValue)
        return instance

