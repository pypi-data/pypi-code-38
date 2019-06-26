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

class Device :
    def __init__( self):
        self.identifier = None
        self.owner = None
        self.type = None
        self.wipeDate = None
        self.wipeBy = None
        self.unwipeDate = None
        self.unwipeBy = None
        self.isWipe = None
        self.hasPartnership = None
        self.policy = None
        self.lastSync = None
        pass

class __DeviceSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Device()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        identifierValue = value['identifier']
        instance.identifier = serder.STRING.parse(identifierValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        typeValue = value['type']
        instance.type = serder.STRING.parse(typeValue)
        wipeDateValue = value['wipeDate']
        instance.wipeDate = serder.DATE.parse(wipeDateValue)
        wipeByValue = value['wipeBy']
        instance.wipeBy = serder.STRING.parse(wipeByValue)
        unwipeDateValue = value['unwipeDate']
        instance.unwipeDate = serder.DATE.parse(unwipeDateValue)
        unwipeByValue = value['unwipeBy']
        instance.unwipeBy = serder.STRING.parse(unwipeByValue)
        isWipeValue = value['isWipe']
        instance.isWipe = serder.BOOLEAN.parse(isWipeValue)
        hasPartnershipValue = value['hasPartnership']
        instance.hasPartnership = serder.BOOLEAN.parse(hasPartnershipValue)
        policyValue = value['policy']
        instance.policy = serder.INT.parse(policyValue)
        lastSyncValue = value['lastSync']
        instance.lastSync = serder.DATE.parse(lastSyncValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        identifierValue = value.identifier
        instance["identifier"] = serder.STRING.encode(identifierValue)
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        typeValue = value.type
        instance["type"] = serder.STRING.encode(typeValue)
        wipeDateValue = value.wipeDate
        instance["wipeDate"] = serder.DATE.encode(wipeDateValue)
        wipeByValue = value.wipeBy
        instance["wipeBy"] = serder.STRING.encode(wipeByValue)
        unwipeDateValue = value.unwipeDate
        instance["unwipeDate"] = serder.DATE.encode(unwipeDateValue)
        unwipeByValue = value.unwipeBy
        instance["unwipeBy"] = serder.STRING.encode(unwipeByValue)
        isWipeValue = value.isWipe
        instance["isWipe"] = serder.BOOLEAN.encode(isWipeValue)
        hasPartnershipValue = value.hasPartnership
        instance["hasPartnership"] = serder.BOOLEAN.encode(hasPartnershipValue)
        policyValue = value.policy
        instance["policy"] = serder.INT.encode(policyValue)
        lastSyncValue = value.lastSync
        instance["lastSync"] = serder.DATE.encode(lastSyncValue)
        return instance

