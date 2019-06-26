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

class ContainerUpdatesResultInError :
    def __init__( self):
        self.message = None
        self.uid = None
        self.errorCode = None
        pass

class __ContainerUpdatesResultInErrorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerUpdatesResultInError()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        from netbluemind.core.api.fault.ErrorCode import ErrorCode
        from netbluemind.core.api.fault.ErrorCode import __ErrorCodeSerDer__
        errorCodeValue = value['errorCode']
        instance.errorCode = __ErrorCodeSerDer__().parse(errorCodeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        uidValue = value.uid
        instance["uid"] = serder.STRING.encode(uidValue)
        from netbluemind.core.api.fault.ErrorCode import ErrorCode
        from netbluemind.core.api.fault.ErrorCode import __ErrorCodeSerDer__
        errorCodeValue = value.errorCode
        instance["errorCode"] = __ErrorCodeSerDer__().encode(errorCodeValue)
        return instance

