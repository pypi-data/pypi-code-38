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

class MailboxFolder :
    def __init__( self):
        self.name = None
        self.fullName = None
        self.parentUid = None
        self.deleted = None
        pass

class __MailboxFolderSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailboxFolder()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        fullNameValue = value['fullName']
        instance.fullName = serder.STRING.parse(fullNameValue)
        parentUidValue = value['parentUid']
        instance.parentUid = serder.STRING.parse(parentUidValue)
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

        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        fullNameValue = value.fullName
        instance["fullName"] = serder.STRING.encode(fullNameValue)
        parentUidValue = value.parentUid
        instance["parentUid"] = serder.STRING.encode(parentUidValue)
        deletedValue = value.deleted
        instance["deleted"] = serder.BOOLEAN.encode(deletedValue)
        return instance

