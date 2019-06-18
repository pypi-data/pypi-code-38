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

from netbluemind.core.container.model.ChangeLogEntry import ChangeLogEntry
from netbluemind.core.container.model.ChangeLogEntry import __ChangeLogEntrySerDer__
class ItemChangeLogEntry (ChangeLogEntry):
    def __init__( self):
        ChangeLogEntry.__init__(self)
        self.authorDisplayName = None
        pass

class __ItemChangeLogEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ItemChangeLogEntry()
        __ChangeLogEntrySerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        authorDisplayNameValue = value['authorDisplayName']
        instance.authorDisplayName = serder.STRING.parse(authorDisplayNameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __ChangeLogEntrySerDer__().encodeInternal(value,instance)

        authorDisplayNameValue = value.authorDisplayName
        instance["authorDisplayName"] = serder.STRING.encode(authorDisplayNameValue)
        return instance

