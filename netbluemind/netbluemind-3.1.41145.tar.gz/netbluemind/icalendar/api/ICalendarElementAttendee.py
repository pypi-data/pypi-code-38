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

class ICalendarElementAttendee :
    def __init__( self):
        self.cutype = None
        self.member = None
        self.role = None
        self.partStatus = None
        self.rsvp = None
        self.delTo = None
        self.delFrom = None
        self.sentBy = None
        self.commonName = None
        self.dir = None
        self.lang = None
        self.mailto = None
        self.uri = None
        self.internal = None
        self.responseComment = None
        pass

class __ICalendarElementAttendeeSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ICalendarElementAttendee()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.icalendar.api.ICalendarElementCUType import ICalendarElementCUType
        from netbluemind.icalendar.api.ICalendarElementCUType import __ICalendarElementCUTypeSerDer__
        cutypeValue = value['cutype']
        instance.cutype = __ICalendarElementCUTypeSerDer__().parse(cutypeValue)
        memberValue = value['member']
        instance.member = serder.STRING.parse(memberValue)
        from netbluemind.icalendar.api.ICalendarElementRole import ICalendarElementRole
        from netbluemind.icalendar.api.ICalendarElementRole import __ICalendarElementRoleSerDer__
        roleValue = value['role']
        instance.role = __ICalendarElementRoleSerDer__().parse(roleValue)
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import ICalendarElementParticipationStatus
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import __ICalendarElementParticipationStatusSerDer__
        partStatusValue = value['partStatus']
        instance.partStatus = __ICalendarElementParticipationStatusSerDer__().parse(partStatusValue)
        rsvpValue = value['rsvp']
        instance.rsvp = serder.BOOLEAN.parse(rsvpValue)
        delToValue = value['delTo']
        instance.delTo = serder.STRING.parse(delToValue)
        delFromValue = value['delFrom']
        instance.delFrom = serder.STRING.parse(delFromValue)
        sentByValue = value['sentBy']
        instance.sentBy = serder.STRING.parse(sentByValue)
        commonNameValue = value['commonName']
        instance.commonName = serder.STRING.parse(commonNameValue)
        dirValue = value['dir']
        instance.dir = serder.STRING.parse(dirValue)
        langValue = value['lang']
        instance.lang = serder.STRING.parse(langValue)
        mailtoValue = value['mailto']
        instance.mailto = serder.STRING.parse(mailtoValue)
        uriValue = value['uri']
        instance.uri = serder.STRING.parse(uriValue)
        internalValue = value['internal']
        instance.internal = serder.BOOLEAN.parse(internalValue)
        responseCommentValue = value['responseComment']
        instance.responseComment = serder.STRING.parse(responseCommentValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.icalendar.api.ICalendarElementCUType import ICalendarElementCUType
        from netbluemind.icalendar.api.ICalendarElementCUType import __ICalendarElementCUTypeSerDer__
        cutypeValue = value.cutype
        instance["cutype"] = __ICalendarElementCUTypeSerDer__().encode(cutypeValue)
        memberValue = value.member
        instance["member"] = serder.STRING.encode(memberValue)
        from netbluemind.icalendar.api.ICalendarElementRole import ICalendarElementRole
        from netbluemind.icalendar.api.ICalendarElementRole import __ICalendarElementRoleSerDer__
        roleValue = value.role
        instance["role"] = __ICalendarElementRoleSerDer__().encode(roleValue)
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import ICalendarElementParticipationStatus
        from netbluemind.icalendar.api.ICalendarElementParticipationStatus import __ICalendarElementParticipationStatusSerDer__
        partStatusValue = value.partStatus
        instance["partStatus"] = __ICalendarElementParticipationStatusSerDer__().encode(partStatusValue)
        rsvpValue = value.rsvp
        instance["rsvp"] = serder.BOOLEAN.encode(rsvpValue)
        delToValue = value.delTo
        instance["delTo"] = serder.STRING.encode(delToValue)
        delFromValue = value.delFrom
        instance["delFrom"] = serder.STRING.encode(delFromValue)
        sentByValue = value.sentBy
        instance["sentBy"] = serder.STRING.encode(sentByValue)
        commonNameValue = value.commonName
        instance["commonName"] = serder.STRING.encode(commonNameValue)
        dirValue = value.dir
        instance["dir"] = serder.STRING.encode(dirValue)
        langValue = value.lang
        instance["lang"] = serder.STRING.encode(langValue)
        mailtoValue = value.mailto
        instance["mailto"] = serder.STRING.encode(mailtoValue)
        uriValue = value.uri
        instance["uri"] = serder.STRING.encode(uriValue)
        internalValue = value.internal
        instance["internal"] = serder.BOOLEAN.encode(internalValue)
        responseCommentValue = value.responseComment
        instance["responseComment"] = serder.STRING.encode(responseCommentValue)
        return instance

