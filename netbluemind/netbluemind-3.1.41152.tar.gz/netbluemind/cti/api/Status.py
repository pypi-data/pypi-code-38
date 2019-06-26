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

class Status :
    def __init__( self):
        self.type = None
        self.message = None
        self.phoneState = None
        pass

class __StatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Status()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.cti.api.StatusType import StatusType
        from netbluemind.cti.api.StatusType import __StatusTypeSerDer__
        typeValue = value['type']
        instance.type = __StatusTypeSerDer__().parse(typeValue)
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        from netbluemind.cti.api.StatusPhoneState import StatusPhoneState
        from netbluemind.cti.api.StatusPhoneState import __StatusPhoneStateSerDer__
        phoneStateValue = value['phoneState']
        instance.phoneState = __StatusPhoneStateSerDer__().parse(phoneStateValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.cti.api.StatusType import StatusType
        from netbluemind.cti.api.StatusType import __StatusTypeSerDer__
        typeValue = value.type
        instance["type"] = __StatusTypeSerDer__().encode(typeValue)
        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        from netbluemind.cti.api.StatusPhoneState import StatusPhoneState
        from netbluemind.cti.api.StatusPhoneState import __StatusPhoneStateSerDer__
        phoneStateValue = value.phoneState
        instance["phoneState"] = __StatusPhoneStateSerDer__().encode(phoneStateValue)
        return instance

