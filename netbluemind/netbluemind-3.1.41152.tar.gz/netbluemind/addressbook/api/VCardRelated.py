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

class VCardRelated :
    def __init__( self):
        self.spouse = None
        self.manager = None
        self.assistant = None
        pass

class __VCardRelatedSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardRelated()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        spouseValue = value['spouse']
        instance.spouse = serder.STRING.parse(spouseValue)
        managerValue = value['manager']
        instance.manager = serder.STRING.parse(managerValue)
        assistantValue = value['assistant']
        instance.assistant = serder.STRING.parse(assistantValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        spouseValue = value.spouse
        instance["spouse"] = serder.STRING.encode(spouseValue)
        managerValue = value.manager
        instance["manager"] = serder.STRING.encode(managerValue)
        assistantValue = value.assistant
        instance["assistant"] = serder.STRING.encode(assistantValue)
        return instance

