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

class DirBaseValue :
    def __init__( self):
        self.orgUnitUid = None
        self.emails = None
        self.hidden = None
        self.archived = None
        self.system = None
        self.dataLocation = None
        pass

class __DirBaseValueSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DirBaseValue()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        orgUnitUidValue = value['orgUnitUid']
        instance.orgUnitUid = serder.STRING.parse(orgUnitUidValue)
        from netbluemind.core.api.Email import Email
        from netbluemind.core.api.Email import __EmailSerDer__
        emailsValue = value['emails']
        instance.emails = serder.CollectionSerDer(__EmailSerDer__()).parse(emailsValue)
        hiddenValue = value['hidden']
        instance.hidden = serder.BOOLEAN.parse(hiddenValue)
        archivedValue = value['archived']
        instance.archived = serder.BOOLEAN.parse(archivedValue)
        systemValue = value['system']
        instance.system = serder.BOOLEAN.parse(systemValue)
        dataLocationValue = value['dataLocation']
        instance.dataLocation = serder.STRING.parse(dataLocationValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        orgUnitUidValue = value.orgUnitUid
        instance["orgUnitUid"] = serder.STRING.encode(orgUnitUidValue)
        from netbluemind.core.api.Email import Email
        from netbluemind.core.api.Email import __EmailSerDer__
        emailsValue = value.emails
        instance["emails"] = serder.CollectionSerDer(__EmailSerDer__()).encode(emailsValue)
        hiddenValue = value.hidden
        instance["hidden"] = serder.BOOLEAN.encode(hiddenValue)
        archivedValue = value.archived
        instance["archived"] = serder.BOOLEAN.encode(archivedValue)
        systemValue = value.system
        instance["system"] = serder.BOOLEAN.encode(systemValue)
        dataLocationValue = value.dataLocation
        instance["dataLocation"] = serder.STRING.encode(dataLocationValue)
        return instance

