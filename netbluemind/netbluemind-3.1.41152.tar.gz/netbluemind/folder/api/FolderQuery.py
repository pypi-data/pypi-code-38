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

class FolderQuery :
    def __init__( self):
        self.type = None
        self.name = None
        pass

class __FolderQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = FolderQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.folder.api.FolderType import FolderType
        from netbluemind.folder.api.FolderType import __FolderTypeSerDer__
        typeValue = value['type']
        instance.type = serder.ArraySerDer(__FolderTypeSerDer__()).parse(typeValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.folder.api.FolderType import FolderType
        from netbluemind.folder.api.FolderType import __FolderTypeSerDer__
        typeValue = value.type
        instance["type"] = serder.ArraySerDer(__FolderTypeSerDer__()).encode(typeValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        return instance

