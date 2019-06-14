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

class ContainerSyncResult :
    def __init__( self):
        self.status = None
        self.added = None
        self.updated = None
        self.removed = None
        pass

class __ContainerSyncResultSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerSyncResult()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.container.model.ContainerSyncStatus import ContainerSyncStatus
        from netbluemind.core.container.model.ContainerSyncStatus import __ContainerSyncStatusSerDer__
        statusValue = value['status']
        instance.status = __ContainerSyncStatusSerDer__().parse(statusValue)
        addedValue = value['added']
        instance.added = serder.INT.parse(addedValue)
        updatedValue = value['updated']
        instance.updated = serder.INT.parse(updatedValue)
        removedValue = value['removed']
        instance.removed = serder.INT.parse(removedValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.container.model.ContainerSyncStatus import ContainerSyncStatus
        from netbluemind.core.container.model.ContainerSyncStatus import __ContainerSyncStatusSerDer__
        statusValue = value.status
        instance["status"] = __ContainerSyncStatusSerDer__().encode(statusValue)
        addedValue = value.added
        instance["added"] = serder.INT.encode(addedValue)
        updatedValue = value.updated
        instance["updated"] = serder.INT.encode(updatedValue)
        removedValue = value.removed
        instance["removed"] = serder.INT.encode(removedValue)
        return instance

