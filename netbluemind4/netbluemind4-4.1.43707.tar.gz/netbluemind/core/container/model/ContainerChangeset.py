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

class ContainerChangeset :
    def __init__( self):
        self.created = None
        self.updated = None
        self.deleted = None
        self.version = None
        pass

class __ContainerChangesetSerDer__:
    def __init__( self  , T):
        self.paramSerDerT = T
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerChangeset()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        createdValue = value['created']
        instance.created = serder.ListSerDer(self.paramSerDerT).parse(createdValue)
        updatedValue = value['updated']
        instance.updated = serder.ListSerDer(self.paramSerDerT).parse(updatedValue)
        deletedValue = value['deleted']
        instance.deleted = serder.ListSerDer(self.paramSerDerT).parse(deletedValue)
        versionValue = value['version']
        instance.version = serder.LONG.parse(versionValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        createdValue = value.created
        instance["created"] = serder.ListSerDer(self.paramSerDerT).encode(createdValue)
        updatedValue = value.updated
        instance["updated"] = serder.ListSerDer(self.paramSerDerT).encode(updatedValue)
        deletedValue = value.deleted
        instance["deleted"] = serder.ListSerDer(self.paramSerDerT).encode(deletedValue)
        versionValue = value.version
        instance["version"] = serder.LONG.encode(versionValue)
        return instance

