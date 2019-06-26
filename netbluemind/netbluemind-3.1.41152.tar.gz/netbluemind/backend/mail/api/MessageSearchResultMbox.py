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

class MessageSearchResultMbox :
    def __init__( self):
        self.displayName = None
        self.address = None
        self.routingType = None
        pass

class __MessageSearchResultMboxSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MessageSearchResultMbox()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        displayNameValue = value['displayName']
        instance.displayName = serder.STRING.parse(displayNameValue)
        addressValue = value['address']
        instance.address = serder.STRING.parse(addressValue)
        routingTypeValue = value['routingType']
        instance.routingType = serder.STRING.parse(routingTypeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        displayNameValue = value.displayName
        instance["displayName"] = serder.STRING.encode(displayNameValue)
        addressValue = value.address
        instance["address"] = serder.STRING.encode(addressValue)
        routingTypeValue = value.routingType
        instance["routingType"] = serder.STRING.encode(routingTypeValue)
        return instance

