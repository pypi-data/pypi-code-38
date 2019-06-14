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

from netbluemind.addressbook.api.VCardBasicAttribute import VCardBasicAttribute
from netbluemind.addressbook.api.VCardBasicAttribute import __VCardBasicAttributeSerDer__
class VCardDeliveryAddressingAddress (VCardBasicAttribute):
    def __init__( self):
        VCardBasicAttribute.__init__(self)
        self.postOfficeBox = None
        self.extentedAddress = None
        self.streetAddress = None
        self.locality = None
        self.region = None
        self.postalCode = None
        self.countryName = None
        pass

class __VCardDeliveryAddressingAddressSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardDeliveryAddressingAddress()
        __VCardBasicAttributeSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        postOfficeBoxValue = value['postOfficeBox']
        instance.postOfficeBox = serder.STRING.parse(postOfficeBoxValue)
        extentedAddressValue = value['extentedAddress']
        instance.extentedAddress = serder.STRING.parse(extentedAddressValue)
        streetAddressValue = value['streetAddress']
        instance.streetAddress = serder.STRING.parse(streetAddressValue)
        localityValue = value['locality']
        instance.locality = serder.STRING.parse(localityValue)
        regionValue = value['region']
        instance.region = serder.STRING.parse(regionValue)
        postalCodeValue = value['postalCode']
        instance.postalCode = serder.STRING.parse(postalCodeValue)
        countryNameValue = value['countryName']
        instance.countryName = serder.STRING.parse(countryNameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __VCardBasicAttributeSerDer__().encodeInternal(value,instance)

        postOfficeBoxValue = value.postOfficeBox
        instance["postOfficeBox"] = serder.STRING.encode(postOfficeBoxValue)
        extentedAddressValue = value.extentedAddress
        instance["extentedAddress"] = serder.STRING.encode(extentedAddressValue)
        streetAddressValue = value.streetAddress
        instance["streetAddress"] = serder.STRING.encode(streetAddressValue)
        localityValue = value.locality
        instance["locality"] = serder.STRING.encode(localityValue)
        regionValue = value.region
        instance["region"] = serder.STRING.encode(regionValue)
        postalCodeValue = value.postalCode
        instance["postalCode"] = serder.STRING.encode(postalCodeValue)
        countryNameValue = value.countryName
        instance["countryName"] = serder.STRING.encode(countryNameValue)
        return instance

