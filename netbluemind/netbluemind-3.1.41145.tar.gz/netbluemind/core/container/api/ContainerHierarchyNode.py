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

class ContainerHierarchyNode :
    def __init__( self):
        self.containerUid = None
        self.containerType = None
        self.name = None
        self.deleted = None
        pass

class __ContainerHierarchyNodeSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerHierarchyNode()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        containerUidValue = value['containerUid']
        instance.containerUid = serder.STRING.parse(containerUidValue)
        containerTypeValue = value['containerType']
        instance.containerType = serder.STRING.parse(containerTypeValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        deletedValue = value['deleted']
        instance.deleted = serder.BOOLEAN.parse(deletedValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        containerUidValue = value.containerUid
        instance["containerUid"] = serder.STRING.encode(containerUidValue)
        containerTypeValue = value.containerType
        instance["containerType"] = serder.STRING.encode(containerTypeValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        deletedValue = value.deleted
        instance["deleted"] = serder.BOOLEAN.encode(deletedValue)
        return instance

