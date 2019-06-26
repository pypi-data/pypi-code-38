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

class CalendarViewChanges :
    def __init__( self):
        self.add = None
        self.modify = None
        self.delete = None
        pass

class __CalendarViewChangesSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = CalendarViewChanges()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.calendar.api.CalendarViewChangesItemAdd import CalendarViewChangesItemAdd
        from netbluemind.calendar.api.CalendarViewChangesItemAdd import __CalendarViewChangesItemAddSerDer__
        addValue = value['add']
        instance.add = serder.ListSerDer(__CalendarViewChangesItemAddSerDer__()).parse(addValue)
        from netbluemind.calendar.api.CalendarViewChangesItemModify import CalendarViewChangesItemModify
        from netbluemind.calendar.api.CalendarViewChangesItemModify import __CalendarViewChangesItemModifySerDer__
        modifyValue = value['modify']
        instance.modify = serder.ListSerDer(__CalendarViewChangesItemModifySerDer__()).parse(modifyValue)
        from netbluemind.calendar.api.CalendarViewChangesItemDelete import CalendarViewChangesItemDelete
        from netbluemind.calendar.api.CalendarViewChangesItemDelete import __CalendarViewChangesItemDeleteSerDer__
        deleteValue = value['delete']
        instance.delete = serder.ListSerDer(__CalendarViewChangesItemDeleteSerDer__()).parse(deleteValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.calendar.api.CalendarViewChangesItemAdd import CalendarViewChangesItemAdd
        from netbluemind.calendar.api.CalendarViewChangesItemAdd import __CalendarViewChangesItemAddSerDer__
        addValue = value.add
        instance["add"] = serder.ListSerDer(__CalendarViewChangesItemAddSerDer__()).encode(addValue)
        from netbluemind.calendar.api.CalendarViewChangesItemModify import CalendarViewChangesItemModify
        from netbluemind.calendar.api.CalendarViewChangesItemModify import __CalendarViewChangesItemModifySerDer__
        modifyValue = value.modify
        instance["modify"] = serder.ListSerDer(__CalendarViewChangesItemModifySerDer__()).encode(modifyValue)
        from netbluemind.calendar.api.CalendarViewChangesItemDelete import CalendarViewChangesItemDelete
        from netbluemind.calendar.api.CalendarViewChangesItemDelete import __CalendarViewChangesItemDeleteSerDer__
        deleteValue = value.delete
        instance["delete"] = serder.ListSerDer(__CalendarViewChangesItemDeleteSerDer__()).encode(deleteValue)
        return instance

