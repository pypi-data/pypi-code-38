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

from netbluemind.directory.api.DirBaseValue import DirBaseValue
from netbluemind.directory.api.DirBaseValue import __DirBaseValueSerDer__
class ResourceDescriptor (DirBaseValue):
    def __init__( self):
        DirBaseValue.__init__(self)
        self.label = None
        self.typeIdentifier = None
        self.description = None
        self.reservationMode = None
        self.properties = None
        pass

class __ResourceDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ResourceDescriptor()
        __DirBaseValueSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        labelValue = value['label']
        instance.label = serder.STRING.parse(labelValue)
        typeIdentifierValue = value['typeIdentifier']
        instance.typeIdentifier = serder.STRING.parse(typeIdentifierValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        from netbluemind.resource.api.ResourceReservationMode import ResourceReservationMode
        from netbluemind.resource.api.ResourceReservationMode import __ResourceReservationModeSerDer__
        reservationModeValue = value['reservationMode']
        instance.reservationMode = __ResourceReservationModeSerDer__().parse(reservationModeValue)
        from netbluemind.resource.api.ResourceDescriptorPropertyValue import ResourceDescriptorPropertyValue
        from netbluemind.resource.api.ResourceDescriptorPropertyValue import __ResourceDescriptorPropertyValueSerDer__
        propertiesValue = value['properties']
        instance.properties = serder.ListSerDer(__ResourceDescriptorPropertyValueSerDer__()).parse(propertiesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __DirBaseValueSerDer__().encodeInternal(value,instance)

        labelValue = value.label
        instance["label"] = serder.STRING.encode(labelValue)
        typeIdentifierValue = value.typeIdentifier
        instance["typeIdentifier"] = serder.STRING.encode(typeIdentifierValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        from netbluemind.resource.api.ResourceReservationMode import ResourceReservationMode
        from netbluemind.resource.api.ResourceReservationMode import __ResourceReservationModeSerDer__
        reservationModeValue = value.reservationMode
        instance["reservationMode"] = __ResourceReservationModeSerDer__().encode(reservationModeValue)
        from netbluemind.resource.api.ResourceDescriptorPropertyValue import ResourceDescriptorPropertyValue
        from netbluemind.resource.api.ResourceDescriptorPropertyValue import __ResourceDescriptorPropertyValueSerDer__
        propertiesValue = value.properties
        instance["properties"] = serder.ListSerDer(__ResourceDescriptorPropertyValueSerDer__()).encode(propertiesValue)
        return instance

