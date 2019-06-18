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

class Folder :
    def __init__( self):
        self.uid = None
        self.id = None
        self.owner = None
        self.parentId = None
        self.name = None
        self.type = None
        self.contentUri = None
        self.path = None
        pass

class __FolderSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Folder()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uidValue = value['uid']
        instance.uid = serder.LONG.parse(uidValue)
        idValue = value['id']
        instance.id = serder.LONG.parse(idValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        parentIdValue = value['parentId']
        instance.parentId = serder.LONG.parse(parentIdValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        from netbluemind.folder.api.FolderType import FolderType
        from netbluemind.folder.api.FolderType import __FolderTypeSerDer__
        typeValue = value['type']
        instance.type = __FolderTypeSerDer__().parse(typeValue)
        contentUriValue = value['contentUri']
        instance.contentUri = serder.STRING.parse(contentUriValue)
        pathValue = value['path']
        instance.path = serder.STRING.parse(pathValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        uidValue = value.uid
        instance["uid"] = serder.LONG.encode(uidValue)
        idValue = value.id
        instance["id"] = serder.LONG.encode(idValue)
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        parentIdValue = value.parentId
        instance["parentId"] = serder.LONG.encode(parentIdValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        from netbluemind.folder.api.FolderType import FolderType
        from netbluemind.folder.api.FolderType import __FolderTypeSerDer__
        typeValue = value.type
        instance["type"] = __FolderTypeSerDer__().encode(typeValue)
        contentUriValue = value.contentUri
        instance["contentUri"] = serder.STRING.encode(contentUriValue)
        pathValue = value.path
        instance["path"] = serder.STRING.encode(pathValue)
        return instance

