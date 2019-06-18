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

class AddressBookDescriptor :
    def __init__( self):
        self.name = None
        self.domainUid = None
        self.owner = None
        self.system = None
        self.settings = None
        self.orgUnitUid = None
        self.expectedId = None
        pass

class __AddressBookDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = AddressBookDescriptor()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        domainUidValue = value['domainUid']
        instance.domainUid = serder.STRING.parse(domainUidValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        systemValue = value['system']
        instance.system = serder.BOOLEAN.parse(systemValue)
        settingsValue = value['settings']
        instance.settings = serder.MapSerDer(serder.STRING).parse(settingsValue)
        orgUnitUidValue = value['orgUnitUid']
        instance.orgUnitUid = serder.STRING.parse(orgUnitUidValue)
        expectedIdValue = value['expectedId']
        instance.expectedId = serder.LONG.parse(expectedIdValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        domainUidValue = value.domainUid
        instance["domainUid"] = serder.STRING.encode(domainUidValue)
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        systemValue = value.system
        instance["system"] = serder.BOOLEAN.encode(systemValue)
        settingsValue = value.settings
        instance["settings"] = serder.MapSerDer(serder.STRING).encode(settingsValue)
        orgUnitUidValue = value.orgUnitUid
        instance["orgUnitUid"] = serder.STRING.encode(orgUnitUidValue)
        expectedIdValue = value.expectedId
        instance["expectedId"] = serder.LONG.encode(expectedIdValue)
        return instance

