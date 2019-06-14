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

class DocumentMetadata :
    def __init__( self):
        self.uid = None
        self.filename = None
        self.name = None
        self.description = None
        self.mime = None
        pass

class __DocumentMetadataSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DocumentMetadata()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uidValue = value['uid']
        instance.uid = serder.STRING.parse(uidValue)
        filenameValue = value['filename']
        instance.filename = serder.STRING.parse(filenameValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        mimeValue = value['mime']
        instance.mime = serder.STRING.parse(mimeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        uidValue = value.uid
        instance["uid"] = serder.STRING.encode(uidValue)
        filenameValue = value.filename
        instance["filename"] = serder.STRING.encode(filenameValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        mimeValue = value.mime
        instance["mime"] = serder.STRING.encode(mimeValue)
        return instance

