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
class VCardIdentificationName (VCardBasicAttribute):
    def __init__( self):
        VCardBasicAttribute.__init__(self)
        self.familyNames = None
        self.givenNames = None
        self.additionalNames = None
        self.prefixes = None
        self.suffixes = None
        pass

class __VCardIdentificationNameSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardIdentificationName()
        __VCardBasicAttributeSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        familyNamesValue = value['familyNames']
        instance.familyNames = serder.STRING.parse(familyNamesValue)
        givenNamesValue = value['givenNames']
        instance.givenNames = serder.STRING.parse(givenNamesValue)
        additionalNamesValue = value['additionalNames']
        instance.additionalNames = serder.STRING.parse(additionalNamesValue)
        prefixesValue = value['prefixes']
        instance.prefixes = serder.STRING.parse(prefixesValue)
        suffixesValue = value['suffixes']
        instance.suffixes = serder.STRING.parse(suffixesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __VCardBasicAttributeSerDer__().encodeInternal(value,instance)

        familyNamesValue = value.familyNames
        instance["familyNames"] = serder.STRING.encode(familyNamesValue)
        givenNamesValue = value.givenNames
        instance["givenNames"] = serder.STRING.encode(givenNamesValue)
        additionalNamesValue = value.additionalNames
        instance["additionalNames"] = serder.STRING.encode(additionalNamesValue)
        prefixesValue = value.prefixes
        instance["prefixes"] = serder.STRING.encode(prefixesValue)
        suffixesValue = value.suffixes
        instance["suffixes"] = serder.STRING.encode(suffixesValue)
        return instance

