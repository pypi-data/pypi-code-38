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

class VCardSecurity :
    def __init__( self):
        self.key = None
        pass

class __VCardSecuritySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardSecurity()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardSecurityKey import VCardSecurityKey
        from netbluemind.addressbook.api.VCardSecurityKey import __VCardSecurityKeySerDer__
        keyValue = value['key']
        instance.key = __VCardSecurityKeySerDer__().parse(keyValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardSecurityKey import VCardSecurityKey
        from netbluemind.addressbook.api.VCardSecurityKey import __VCardSecurityKeySerDer__
        keyValue = value.key
        instance["key"] = __VCardSecurityKeySerDer__().encode(keyValue)
        return instance

