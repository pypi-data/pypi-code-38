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

class ResourceTypeDescriptor :
    def __init__( self):
        self.label = None
        self.properties = None
        pass

class __ResourceTypeDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ResourceTypeDescriptor()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        labelValue = value['label']
        instance.label = serder.STRING.parse(labelValue)
        from netbluemind.resource.api.type.ResourceTypeDescriptorProperty import ResourceTypeDescriptorProperty
        from netbluemind.resource.api.type.ResourceTypeDescriptorProperty import __ResourceTypeDescriptorPropertySerDer__
        propertiesValue = value['properties']
        instance.properties = serder.ListSerDer(__ResourceTypeDescriptorPropertySerDer__()).parse(propertiesValue)
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
        from netbluemind.resource.api.type.ResourceTypeDescriptorProperty import ResourceTypeDescriptorProperty
        from netbluemind.resource.api.type.ResourceTypeDescriptorProperty import __ResourceTypeDescriptorPropertySerDer__
        propertiesValue = value.properties
        instance["properties"] = serder.ListSerDer(__ResourceTypeDescriptorPropertySerDer__()).encode(propertiesValue)
        return instance

