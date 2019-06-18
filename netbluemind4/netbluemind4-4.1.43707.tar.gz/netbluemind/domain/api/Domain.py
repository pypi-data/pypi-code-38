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

class Domain :
    def __init__( self):
        self.label = None
        self.name = None
        self.description = None
        self.properties = None
        self.global_ = None
        self.aliases = None
        pass

class __DomainSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Domain()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        labelValue = value['label']
        instance.label = serder.STRING.parse(labelValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        propertiesValue = value['properties']
        instance.properties = serder.MapSerDer(serder.STRING).parse(propertiesValue)
        global_Value = value['global']
        instance.global_ = serder.BOOLEAN.parse(global_Value)
        aliasesValue = value['aliases']
        instance.aliases = serder.SetSerDer(serder.STRING).parse(aliasesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        labelValue = value.label
        instance["label"] = serder.STRING.encode(labelValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        propertiesValue = value.properties
        instance["properties"] = serder.MapSerDer(serder.STRING).encode(propertiesValue)
        global_Value = value.global_
        instance["global"] = serder.BOOLEAN.encode(global_Value)
        aliasesValue = value.aliases
        instance["aliases"] = serder.SetSerDer(serder.STRING).encode(aliasesValue)
        return instance

