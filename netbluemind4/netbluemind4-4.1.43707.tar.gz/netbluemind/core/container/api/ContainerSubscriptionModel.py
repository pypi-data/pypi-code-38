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

from netbluemind.core.container.api.ContainerSubscription import ContainerSubscription
from netbluemind.core.container.api.ContainerSubscription import __ContainerSubscriptionSerDer__
class ContainerSubscriptionModel (ContainerSubscription):
    def __init__( self):
        ContainerSubscription.__init__(self)
        self.containerType = None
        self.owner = None
        self.defaultContainer = None
        self.name = None
        pass

class __ContainerSubscriptionModelSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ContainerSubscriptionModel()
        __ContainerSubscriptionSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        containerTypeValue = value['containerType']
        instance.containerType = serder.STRING.parse(containerTypeValue)
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        defaultContainerValue = value['defaultContainer']
        instance.defaultContainer = serder.BOOLEAN.parse(defaultContainerValue)
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
        __ContainerSubscriptionSerDer__().encodeInternal(value,instance)

        containerTypeValue = value.containerType
        instance["containerType"] = serder.STRING.encode(containerTypeValue)
        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        defaultContainerValue = value.defaultContainer
        instance["defaultContainer"] = serder.BOOLEAN.encode(defaultContainerValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        return instance

