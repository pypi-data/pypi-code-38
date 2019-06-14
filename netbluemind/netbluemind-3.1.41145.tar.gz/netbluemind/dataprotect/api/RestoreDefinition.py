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

class RestoreDefinition :
    def __init__( self):
        self.generation = None
        self.restoreOperationIdenfitier = None
        self.item = None
        pass

class __RestoreDefinitionSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = RestoreDefinition()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        generationValue = value['generation']
        instance.generation = serder.INT.parse(generationValue)
        restoreOperationIdenfitierValue = value['restoreOperationIdenfitier']
        instance.restoreOperationIdenfitier = serder.STRING.parse(restoreOperationIdenfitierValue)
        from netbluemind.dataprotect.api.Restorable import Restorable
        from netbluemind.dataprotect.api.Restorable import __RestorableSerDer__
        itemValue = value['item']
        instance.item = __RestorableSerDer__().parse(itemValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        generationValue = value.generation
        instance["generation"] = serder.INT.encode(generationValue)
        restoreOperationIdenfitierValue = value.restoreOperationIdenfitier
        instance["restoreOperationIdenfitier"] = serder.STRING.encode(restoreOperationIdenfitierValue)
        from netbluemind.dataprotect.api.Restorable import Restorable
        from netbluemind.dataprotect.api.Restorable import __RestorableSerDer__
        itemValue = value.item
        instance["item"] = __RestorableSerDer__().encode(itemValue)
        return instance

