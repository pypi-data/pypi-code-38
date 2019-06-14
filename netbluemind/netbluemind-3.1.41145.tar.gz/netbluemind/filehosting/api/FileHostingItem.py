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

class FileHostingItem :
    def __init__( self):
        self.path = None
        self.name = None
        self.type = None
        self.size = None
        self.metadata = None
        pass

class __FileHostingItemSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = FileHostingItem()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        pathValue = value['path']
        instance.path = serder.STRING.parse(pathValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        from netbluemind.filehosting.api.FileType import FileType
        from netbluemind.filehosting.api.FileType import __FileTypeSerDer__
        typeValue = value['type']
        instance.type = __FileTypeSerDer__().parse(typeValue)
        sizeValue = value['size']
        instance.size = serder.LONG.parse(sizeValue)
        from netbluemind.filehosting.api.Metadata import Metadata
        from netbluemind.filehosting.api.Metadata import __MetadataSerDer__
        metadataValue = value['metadata']
        instance.metadata = serder.ListSerDer(__MetadataSerDer__()).parse(metadataValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        pathValue = value.path
        instance["path"] = serder.STRING.encode(pathValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        from netbluemind.filehosting.api.FileType import FileType
        from netbluemind.filehosting.api.FileType import __FileTypeSerDer__
        typeValue = value.type
        instance["type"] = __FileTypeSerDer__().encode(typeValue)
        sizeValue = value.size
        instance["size"] = serder.LONG.encode(sizeValue)
        from netbluemind.filehosting.api.Metadata import Metadata
        from netbluemind.filehosting.api.Metadata import __MetadataSerDer__
        metadataValue = value.metadata
        instance["metadata"] = serder.ListSerDer(__MetadataSerDer__()).encode(metadataValue)
        return instance

