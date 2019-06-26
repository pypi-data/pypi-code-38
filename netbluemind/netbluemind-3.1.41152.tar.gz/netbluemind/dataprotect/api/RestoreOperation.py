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

class RestoreOperation :
    def __init__( self):
        self.identifier = None
        self.kind = None
        self.translations = None
        self.requiredTag = None
        pass

class __RestoreOperationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = RestoreOperation()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        identifierValue = value['identifier']
        instance.identifier = serder.STRING.parse(identifierValue)
        from netbluemind.dataprotect.api.RestorableKind import RestorableKind
        from netbluemind.dataprotect.api.RestorableKind import __RestorableKindSerDer__
        kindValue = value['kind']
        instance.kind = __RestorableKindSerDer__().parse(kindValue)
        translationsValue = value['translations']
        instance.translations = serder.MapSerDer(serder.STRING).parse(translationsValue)
        requiredTagValue = value['requiredTag']
        instance.requiredTag = serder.STRING.parse(requiredTagValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        identifierValue = value.identifier
        instance["identifier"] = serder.STRING.encode(identifierValue)
        from netbluemind.dataprotect.api.RestorableKind import RestorableKind
        from netbluemind.dataprotect.api.RestorableKind import __RestorableKindSerDer__
        kindValue = value.kind
        instance["kind"] = __RestorableKindSerDer__().encode(kindValue)
        translationsValue = value.translations
        instance["translations"] = serder.MapSerDer(serder.STRING).encode(translationsValue)
        requiredTagValue = value.requiredTag
        instance["requiredTag"] = serder.STRING.encode(requiredTagValue)
        return instance

