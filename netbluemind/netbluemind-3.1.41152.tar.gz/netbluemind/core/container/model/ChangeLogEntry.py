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

class ChangeLogEntry :
    def __init__( self):
        self.version = None
        self.itemUid = None
        self.itemExtId = None
        self.author = None
        self.type = None
        self.date = None
        self.origin = None
        self.internalId = None
        pass

class __ChangeLogEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ChangeLogEntry()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        versionValue = value['version']
        instance.version = serder.LONG.parse(versionValue)
        itemUidValue = value['itemUid']
        instance.itemUid = serder.STRING.parse(itemUidValue)
        itemExtIdValue = value['itemExtId']
        instance.itemExtId = serder.STRING.parse(itemExtIdValue)
        authorValue = value['author']
        instance.author = serder.STRING.parse(authorValue)
        from netbluemind.core.container.model.ChangeLogEntryType import ChangeLogEntryType
        from netbluemind.core.container.model.ChangeLogEntryType import __ChangeLogEntryTypeSerDer__
        typeValue = value['type']
        instance.type = __ChangeLogEntryTypeSerDer__().parse(typeValue)
        dateValue = value['date']
        instance.date = serder.DATE.parse(dateValue)
        originValue = value['origin']
        instance.origin = serder.STRING.parse(originValue)
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

        versionValue = value.version
        instance["version"] = serder.LONG.encode(versionValue)
        itemUidValue = value.itemUid
        instance["itemUid"] = serder.STRING.encode(itemUidValue)
        itemExtIdValue = value.itemExtId
        instance["itemExtId"] = serder.STRING.encode(itemExtIdValue)
        authorValue = value.author
        instance["author"] = serder.STRING.encode(authorValue)
        from netbluemind.core.container.model.ChangeLogEntryType import ChangeLogEntryType
        from netbluemind.core.container.model.ChangeLogEntryType import __ChangeLogEntryTypeSerDer__
        typeValue = value.type
        instance["type"] = __ChangeLogEntryTypeSerDer__().encode(typeValue)
        dateValue = value.date
        instance["date"] = serder.DATE.encode(dateValue)
        originValue = value.origin
        instance["origin"] = serder.STRING.encode(originValue)
        internalIdValue = value.internalId
        instance["internalId"] = serder.LONG.encode(internalIdValue)
        return instance

