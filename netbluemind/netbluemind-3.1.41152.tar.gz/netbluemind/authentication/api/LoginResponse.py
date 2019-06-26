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

class LoginResponse :
    def __init__( self):
        self.status = None
        self.message = None
        self.authKey = None
        self.latd = None
        self.authUser = None
        pass

class __LoginResponseSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = LoginResponse()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.authentication.api.LoginResponseStatus import LoginResponseStatus
        from netbluemind.authentication.api.LoginResponseStatus import __LoginResponseStatusSerDer__
        statusValue = value['status']
        instance.status = __LoginResponseStatusSerDer__().parse(statusValue)
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        authKeyValue = value['authKey']
        instance.authKey = serder.STRING.parse(authKeyValue)
        latdValue = value['latd']
        instance.latd = serder.STRING.parse(latdValue)
        from netbluemind.authentication.api.AuthUser import AuthUser
        from netbluemind.authentication.api.AuthUser import __AuthUserSerDer__
        authUserValue = value['authUser']
        instance.authUser = __AuthUserSerDer__().parse(authUserValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.authentication.api.LoginResponseStatus import LoginResponseStatus
        from netbluemind.authentication.api.LoginResponseStatus import __LoginResponseStatusSerDer__
        statusValue = value.status
        instance["status"] = __LoginResponseStatusSerDer__().encode(statusValue)
        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        authKeyValue = value.authKey
        instance["authKey"] = serder.STRING.encode(authKeyValue)
        latdValue = value.latd
        instance["latd"] = serder.STRING.encode(latdValue)
        from netbluemind.authentication.api.AuthUser import AuthUser
        from netbluemind.authentication.api.AuthUser import __AuthUserSerDer__
        authUserValue = value.authUser
        instance["authUser"] = __AuthUserSerDer__().encode(authUserValue)
        return instance

