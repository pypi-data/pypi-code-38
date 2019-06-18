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

class StoragePolicy :
    def __init__( self):
        self.daysBeforeMove = None
        self.maxQuota = None
        self.defaultQuota = None
        self.excludedFolders = None
        pass

class __StoragePolicySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = StoragePolicy()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        daysBeforeMoveValue = value['daysBeforeMove']
        instance.daysBeforeMove = serder.INT.parse(daysBeforeMoveValue)
        maxQuotaValue = value['maxQuota']
        instance.maxQuota = serder.INT.parse(maxQuotaValue)
        defaultQuotaValue = value['defaultQuota']
        instance.defaultQuota = serder.INT.parse(defaultQuotaValue)
        excludedFoldersValue = value['excludedFolders']
        instance.excludedFolders = serder.ListSerDer(serder.STRING).parse(excludedFoldersValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        daysBeforeMoveValue = value.daysBeforeMove
        instance["daysBeforeMove"] = serder.INT.encode(daysBeforeMoveValue)
        maxQuotaValue = value.maxQuota
        instance["maxQuota"] = serder.INT.encode(maxQuotaValue)
        defaultQuotaValue = value.defaultQuota
        instance["defaultQuota"] = serder.INT.encode(defaultQuotaValue)
        excludedFoldersValue = value.excludedFolders
        instance["excludedFolders"] = serder.ListSerDer(serder.STRING).encode(excludedFoldersValue)
        return instance

