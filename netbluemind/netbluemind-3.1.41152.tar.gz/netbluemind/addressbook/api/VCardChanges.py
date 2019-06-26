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

class VCardChanges :
    def __init__( self):
        self.add = None
        self.modify = None
        self.delete = None
        pass

class __VCardChangesSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardChanges()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardChangesItemAdd import VCardChangesItemAdd
        from netbluemind.addressbook.api.VCardChangesItemAdd import __VCardChangesItemAddSerDer__
        addValue = value['add']
        instance.add = serder.ListSerDer(__VCardChangesItemAddSerDer__()).parse(addValue)
        from netbluemind.addressbook.api.VCardChangesItemModify import VCardChangesItemModify
        from netbluemind.addressbook.api.VCardChangesItemModify import __VCardChangesItemModifySerDer__
        modifyValue = value['modify']
        instance.modify = serder.ListSerDer(__VCardChangesItemModifySerDer__()).parse(modifyValue)
        from netbluemind.addressbook.api.VCardChangesItemDelete import VCardChangesItemDelete
        from netbluemind.addressbook.api.VCardChangesItemDelete import __VCardChangesItemDeleteSerDer__
        deleteValue = value['delete']
        instance.delete = serder.ListSerDer(__VCardChangesItemDeleteSerDer__()).parse(deleteValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardChangesItemAdd import VCardChangesItemAdd
        from netbluemind.addressbook.api.VCardChangesItemAdd import __VCardChangesItemAddSerDer__
        addValue = value.add
        instance["add"] = serder.ListSerDer(__VCardChangesItemAddSerDer__()).encode(addValue)
        from netbluemind.addressbook.api.VCardChangesItemModify import VCardChangesItemModify
        from netbluemind.addressbook.api.VCardChangesItemModify import __VCardChangesItemModifySerDer__
        modifyValue = value.modify
        instance["modify"] = serder.ListSerDer(__VCardChangesItemModifySerDer__()).encode(modifyValue)
        from netbluemind.addressbook.api.VCardChangesItemDelete import VCardChangesItemDelete
        from netbluemind.addressbook.api.VCardChangesItemDelete import __VCardChangesItemDeleteSerDer__
        deleteValue = value.delete
        instance["delete"] = serder.ListSerDer(__VCardChangesItemDeleteSerDer__()).encode(deleteValue)
        return instance

