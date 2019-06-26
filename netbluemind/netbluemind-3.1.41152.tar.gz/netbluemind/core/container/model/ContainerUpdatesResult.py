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

class ContainerUpdatesResult :
    def __init__( self):
        self.added = None
        self.updated = None
        self.removed = None
        self.errors = None
        self.version = None
        pass

class __ContainerUpdatesResultSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerUpdatesResult()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        addedValue = value['added']
        instance.added = serder.ListSerDer(serder.STRING).parse(addedValue)
        updatedValue = value['updated']
        instance.updated = serder.ListSerDer(serder.STRING).parse(updatedValue)
        removedValue = value['removed']
        instance.removed = serder.ListSerDer(serder.STRING).parse(removedValue)
        from netbluemind.core.container.model.ContainerUpdatesResultInError import ContainerUpdatesResultInError
        from netbluemind.core.container.model.ContainerUpdatesResultInError import __ContainerUpdatesResultInErrorSerDer__
        errorsValue = value['errors']
        instance.errors = serder.ListSerDer(__ContainerUpdatesResultInErrorSerDer__()).parse(errorsValue)
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

        addedValue = value.added
        instance["added"] = serder.ListSerDer(serder.STRING).encode(addedValue)
        updatedValue = value.updated
        instance["updated"] = serder.ListSerDer(serder.STRING).encode(updatedValue)
        removedValue = value.removed
        instance["removed"] = serder.ListSerDer(serder.STRING).encode(removedValue)
        from netbluemind.core.container.model.ContainerUpdatesResultInError import ContainerUpdatesResultInError
        from netbluemind.core.container.model.ContainerUpdatesResultInError import __ContainerUpdatesResultInErrorSerDer__
        errorsValue = value.errors
        instance["errors"] = serder.ListSerDer(__ContainerUpdatesResultInErrorSerDer__()).encode(errorsValue)
        versionValue = value.version
        instance["version"] = serder.LONG.encode(versionValue)
        return instance

