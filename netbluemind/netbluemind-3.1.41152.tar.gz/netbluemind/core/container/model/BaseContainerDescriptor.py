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

class BaseContainerDescriptor :
    def __init__( self):
        self.uid = None
        self.name = None
        self.owner = None
        self.type = None
        self.defaultContainer = None
        self.readOnly = None
        self.domainUid = None
        self.ownerDisplayname = None
        self.ownerDirEntryPath = None
        self.settings = None
        pass

class __BaseContainerDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = BaseContainerDescriptor()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        typeValue = value['type']
        instance.type = serder.STRING.parse(typeValue)
        defaultContainerValue = value['defaultContainer']
        instance.defaultContainer = serder.BOOLEAN.parse(defaultContainerValue)
        readOnlyValue = value['readOnly']
        instance.readOnly = serder.BOOLEAN.parse(readOnlyValue)
        domainUidValue = value['domainUid']
        instance.domainUid = serder.STRING.parse(domainUidValue)
        ownerDisplaynameValue = value['ownerDisplayname']
        instance.ownerDisplayname = serder.STRING.parse(ownerDisplaynameValue)
        ownerDirEntryPathValue = value['ownerDirEntryPath']
        instance.ownerDirEntryPath = serder.STRING.parse(ownerDirEntryPathValue)
        settingsValue = value['settings']
        instance.settings = serder.MapSerDer(serder.STRING).parse(settingsValue)
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
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        typeValue = value.type
        instance["type"] = serder.STRING.encode(typeValue)
        defaultContainerValue = value.defaultContainer
        instance["defaultContainer"] = serder.BOOLEAN.encode(defaultContainerValue)
        readOnlyValue = value.readOnly
        instance["readOnly"] = serder.BOOLEAN.encode(readOnlyValue)
        domainUidValue = value.domainUid
        instance["domainUid"] = serder.STRING.encode(domainUidValue)
        ownerDisplaynameValue = value.ownerDisplayname
        instance["ownerDisplayname"] = serder.STRING.encode(ownerDisplaynameValue)
        ownerDirEntryPathValue = value.ownerDirEntryPath
        instance["ownerDirEntryPath"] = serder.STRING.encode(ownerDirEntryPathValue)
        settingsValue = value.settings
        instance["settings"] = serder.MapSerDer(serder.STRING).encode(settingsValue)
        return instance

