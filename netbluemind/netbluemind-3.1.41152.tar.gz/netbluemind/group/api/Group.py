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
class Group (DirBaseValue):
    def __init__( self):
        DirBaseValue.__init__(self)
        self.name = None
        self.description = None
        self.properties = None
        self.hiddenMembers = None
        self.mailArchived = None
        self.memberCount = None
        pass

class __GroupSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Group()
        __DirBaseValueSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        propertiesValue = value['properties']
        instance.properties = serder.MapSerDer(serder.STRING).parse(propertiesValue)
        hiddenMembersValue = value['hiddenMembers']
        instance.hiddenMembers = serder.BOOLEAN.parse(hiddenMembersValue)
        mailArchivedValue = value['mailArchived']
        instance.mailArchived = serder.BOOLEAN.parse(mailArchivedValue)
        memberCountValue = value['memberCount']
        instance.memberCount = serder.INT.parse(memberCountValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __DirBaseValueSerDer__().encodeInternal(value,instance)

        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        propertiesValue = value.properties
        instance["properties"] = serder.MapSerDer(serder.STRING).encode(propertiesValue)
        hiddenMembersValue = value.hiddenMembers
        instance["hiddenMembers"] = serder.BOOLEAN.encode(hiddenMembersValue)
        mailArchivedValue = value.mailArchived
        instance["mailArchived"] = serder.BOOLEAN.encode(mailArchivedValue)
        memberCountValue = value.memberCount
        instance["memberCount"] = serder.INT.encode(memberCountValue)
        return instance

