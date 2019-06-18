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

from netbluemind.user.api.UserAccount import UserAccount
from netbluemind.user.api.UserAccount import __UserAccountSerDer__
class UserAccountInfo (UserAccount):
    def __init__( self):
        UserAccount.__init__(self)
        self.externalSystemId = None
        pass

class __UserAccountInfoSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = UserAccountInfo()
        __UserAccountSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        externalSystemIdValue = value['externalSystemId']
        instance.externalSystemId = serder.STRING.parse(externalSystemIdValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __UserAccountSerDer__().encodeInternal(value,instance)

        externalSystemIdValue = value.externalSystemId
        instance["externalSystemId"] = serder.STRING.encode(externalSystemIdValue)
        return instance

