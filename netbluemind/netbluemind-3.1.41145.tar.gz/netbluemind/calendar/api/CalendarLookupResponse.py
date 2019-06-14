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

class CalendarLookupResponse :
    def __init__( self):
        self.uid = None
        self.name = None
        self.type = None
        self.email = None
        self.memberCount = None
        self.ownerUid = None
        pass

class __CalendarLookupResponseSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = CalendarLookupResponse()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        from netbluemind.calendar.api.CalendarLookupResponseType import CalendarLookupResponseType
        from netbluemind.calendar.api.CalendarLookupResponseType import __CalendarLookupResponseTypeSerDer__
        typeValue = value['type']
        instance.type = __CalendarLookupResponseTypeSerDer__().parse(typeValue)
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        memberCountValue = value['memberCount']
        instance.memberCount = serder.INT.parse(memberCountValue)
        ownerUidValue = value['ownerUid']
        instance.ownerUid = serder.STRING.parse(ownerUidValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        uidValue = value.uid
        instance["uid"] = serder.STRING.encode(uidValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        from netbluemind.calendar.api.CalendarLookupResponseType import CalendarLookupResponseType
        from netbluemind.calendar.api.CalendarLookupResponseType import __CalendarLookupResponseTypeSerDer__
        typeValue = value.type
        instance["type"] = __CalendarLookupResponseTypeSerDer__().encode(typeValue)
        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        memberCountValue = value.memberCount
        instance["memberCount"] = serder.INT.encode(memberCountValue)
        ownerUidValue = value.ownerUid
        instance["ownerUid"] = serder.STRING.encode(ownerUidValue)
        return instance

