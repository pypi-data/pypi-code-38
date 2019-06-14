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

class ContainerQuery :
    def __init__( self):
        self.type = None
        self.name = None
        self.verb = None
        self.owner = None
        self.readonly = None
        self.size = None
        pass

class __ContainerQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        typeValue = value['type']
        instance.type = serder.STRING.parse(typeValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbValue = value['verb']
        instance.verb = serder.ListSerDer(__VerbSerDer__()).parse(verbValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        readonlyValue = value['readonly']
        instance.readonly = serder.BOOLEAN.parse(readonlyValue)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        typeValue = value.type
        instance["type"] = serder.STRING.encode(typeValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbValue = value.verb
        instance["verb"] = serder.ListSerDer(__VerbSerDer__()).encode(verbValue)
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        readonlyValue = value.readonly
        instance["readonly"] = serder.BOOLEAN.encode(readonlyValue)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        return instance

