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

from netbluemind.directory.api.BaseDirEntry import BaseDirEntry
from netbluemind.directory.api.BaseDirEntry import __BaseDirEntrySerDer__
class DirEntry (BaseDirEntry):
    def __init__( self):
        BaseDirEntry.__init__(self)
        self.path = None
        self.email = None
        self.hidden = None
        self.system = None
        self.archived = None
        self.emails = None
        self.orgUnitUid = None
        self.orgUnitPath = None
        self.dataLocation = None
        pass

class __DirEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DirEntry()
        __BaseDirEntrySerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        pathValue = value['path']
        instance.path = serder.STRING.parse(pathValue)
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        hiddenValue = value['hidden']
        instance.hidden = serder.BOOLEAN.parse(hiddenValue)
        systemValue = value['system']
        instance.system = serder.BOOLEAN.parse(systemValue)
        archivedValue = value['archived']
        instance.archived = serder.BOOLEAN.parse(archivedValue)
        from netbluemind.core.api.Email import Email
        from netbluemind.core.api.Email import __EmailSerDer__
        emailsValue = value['emails']
        instance.emails = serder.ListSerDer(__EmailSerDer__()).parse(emailsValue)
        orgUnitUidValue = value['orgUnitUid']
        instance.orgUnitUid = serder.STRING.parse(orgUnitUidValue)
        from netbluemind.directory.api.OrgUnitPath import OrgUnitPath
        from netbluemind.directory.api.OrgUnitPath import __OrgUnitPathSerDer__
        orgUnitPathValue = value['orgUnitPath']
        instance.orgUnitPath = __OrgUnitPathSerDer__().parse(orgUnitPathValue)
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
        __BaseDirEntrySerDer__().encodeInternal(value,instance)

        pathValue = value.path
        instance["path"] = serder.STRING.encode(pathValue)
        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        hiddenValue = value.hidden
        instance["hidden"] = serder.BOOLEAN.encode(hiddenValue)
        systemValue = value.system
        instance["system"] = serder.BOOLEAN.encode(systemValue)
        archivedValue = value.archived
        instance["archived"] = serder.BOOLEAN.encode(archivedValue)
        from netbluemind.core.api.Email import Email
        from netbluemind.core.api.Email import __EmailSerDer__
        emailsValue = value.emails
        instance["emails"] = serder.ListSerDer(__EmailSerDer__()).encode(emailsValue)
        orgUnitUidValue = value.orgUnitUid
        instance["orgUnitUid"] = serder.STRING.encode(orgUnitUidValue)
        from netbluemind.directory.api.OrgUnitPath import OrgUnitPath
        from netbluemind.directory.api.OrgUnitPath import __OrgUnitPathSerDer__
        orgUnitPathValue = value.orgUnitPath
        instance["orgUnitPath"] = __OrgUnitPathSerDer__().encode(orgUnitPathValue)
        dataLocationValue = value.dataLocation
        instance["dataLocation"] = serder.STRING.encode(dataLocationValue)
        return instance

