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

class ContainerSyncStatus :
    def __init__( self):
        self.syncToken = None
        self.nextSync = None
        self.lastSync = None
        self.syncStatus = None
        pass

class __ContainerSyncStatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerSyncStatus()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        syncTokenValue = value['syncToken']
        instance.syncToken = serder.STRING.parse(syncTokenValue)
        nextSyncValue = value['nextSync']
        instance.nextSync = serder.LONG.parse(nextSyncValue)
        lastSyncValue = value['lastSync']
        instance.lastSync = serder.DATE.parse(lastSyncValue)
        from netbluemind.core.container.model.ContainerSyncStatusStatus import ContainerSyncStatusStatus
        from netbluemind.core.container.model.ContainerSyncStatusStatus import __ContainerSyncStatusStatusSerDer__
        syncStatusValue = value['syncStatus']
        instance.syncStatus = __ContainerSyncStatusStatusSerDer__().parse(syncStatusValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        syncTokenValue = value.syncToken
        instance["syncToken"] = serder.STRING.encode(syncTokenValue)
        nextSyncValue = value.nextSync
        instance["nextSync"] = serder.LONG.encode(nextSyncValue)
        lastSyncValue = value.lastSync
        instance["lastSync"] = serder.DATE.encode(lastSyncValue)
        from netbluemind.core.container.model.ContainerSyncStatusStatus import ContainerSyncStatusStatus
        from netbluemind.core.container.model.ContainerSyncStatusStatus import __ContainerSyncStatusStatusSerDer__
        syncStatusValue = value.syncStatus
        instance["syncStatus"] = __ContainerSyncStatusStatusSerDer__().encode(syncStatusValue)
        return instance

