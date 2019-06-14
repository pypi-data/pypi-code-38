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

class SubscriptionInformationsMessage :
    def __init__( self):
        self.kind = None
        self.code = None
        self.message = None
        pass

class __SubscriptionInformationsMessageSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SubscriptionInformationsMessage()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.system.api.SubscriptionInformationsMessageKind import SubscriptionInformationsMessageKind
        from netbluemind.system.api.SubscriptionInformationsMessageKind import __SubscriptionInformationsMessageKindSerDer__
        kindValue = value['kind']
        instance.kind = __SubscriptionInformationsMessageKindSerDer__().parse(kindValue)
        from netbluemind.system.api.SubscriptionInformationsMessageCode import SubscriptionInformationsMessageCode
        from netbluemind.system.api.SubscriptionInformationsMessageCode import __SubscriptionInformationsMessageCodeSerDer__
        codeValue = value['code']
        instance.code = __SubscriptionInformationsMessageCodeSerDer__().parse(codeValue)
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.system.api.SubscriptionInformationsMessageKind import SubscriptionInformationsMessageKind
        from netbluemind.system.api.SubscriptionInformationsMessageKind import __SubscriptionInformationsMessageKindSerDer__
        kindValue = value.kind
        instance["kind"] = __SubscriptionInformationsMessageKindSerDer__().encode(kindValue)
        from netbluemind.system.api.SubscriptionInformationsMessageCode import SubscriptionInformationsMessageCode
        from netbluemind.system.api.SubscriptionInformationsMessageCode import __SubscriptionInformationsMessageCodeSerDer__
        codeValue = value.code
        instance["code"] = __SubscriptionInformationsMessageCodeSerDer__().encode(codeValue)
        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        return instance

