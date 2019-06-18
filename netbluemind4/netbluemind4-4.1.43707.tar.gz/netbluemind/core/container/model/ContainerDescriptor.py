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

from netbluemind.core.container.model.BaseContainerDescriptor import BaseContainerDescriptor
from netbluemind.core.container.model.BaseContainerDescriptor import __BaseContainerDescriptorSerDer__
class ContainerDescriptor (BaseContainerDescriptor):
    def __init__( self):
        BaseContainerDescriptor.__init__(self)
        self.writable = None
        self.verbs = None
        self.offlineSync = None
        self.internalId = None
        pass

class __ContainerDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerDescriptor()
        __BaseContainerDescriptorSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        writableValue = value['writable']
        instance.writable = serder.BOOLEAN.parse(writableValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbsValue = value['verbs']
        instance.verbs = serder.SetSerDer(__VerbSerDer__()).parse(verbsValue)
        offlineSyncValue = value['offlineSync']
        instance.offlineSync = serder.BOOLEAN.parse(offlineSyncValue)
        internalIdValue = value['internalId']
        instance.internalId = serder.LONG.parse(internalIdValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __BaseContainerDescriptorSerDer__().encodeInternal(value,instance)

        writableValue = value.writable
        instance["writable"] = serder.BOOLEAN.encode(writableValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbsValue = value.verbs
        instance["verbs"] = serder.SetSerDer(__VerbSerDer__()).encode(verbsValue)
        offlineSyncValue = value.offlineSync
        instance["offlineSync"] = serder.BOOLEAN.encode(offlineSyncValue)
        internalIdValue = value.internalId
        instance["internalId"] = serder.LONG.encode(internalIdValue)
        return instance

