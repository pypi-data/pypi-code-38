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

class TagChanges :
    def __init__( self):
        self.add = None
        self.modify = None
        self.delete = None
        pass

class __TagChangesSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = TagChanges()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.tag.api.TagChangesItemAdd import TagChangesItemAdd
        from netbluemind.tag.api.TagChangesItemAdd import __TagChangesItemAddSerDer__
        addValue = value['add']
        instance.add = serder.ListSerDer(__TagChangesItemAddSerDer__()).parse(addValue)
        from netbluemind.tag.api.TagChangesItemModify import TagChangesItemModify
        from netbluemind.tag.api.TagChangesItemModify import __TagChangesItemModifySerDer__
        modifyValue = value['modify']
        instance.modify = serder.ListSerDer(__TagChangesItemModifySerDer__()).parse(modifyValue)
        from netbluemind.tag.api.TagChangesItemDelete import TagChangesItemDelete
        from netbluemind.tag.api.TagChangesItemDelete import __TagChangesItemDeleteSerDer__
        deleteValue = value['delete']
        instance.delete = serder.ListSerDer(__TagChangesItemDeleteSerDer__()).parse(deleteValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.tag.api.TagChangesItemAdd import TagChangesItemAdd
        from netbluemind.tag.api.TagChangesItemAdd import __TagChangesItemAddSerDer__
        addValue = value.add
        instance["add"] = serder.ListSerDer(__TagChangesItemAddSerDer__()).encode(addValue)
        from netbluemind.tag.api.TagChangesItemModify import TagChangesItemModify
        from netbluemind.tag.api.TagChangesItemModify import __TagChangesItemModifySerDer__
        modifyValue = value.modify
        instance["modify"] = serder.ListSerDer(__TagChangesItemModifySerDer__()).encode(modifyValue)
        from netbluemind.tag.api.TagChangesItemDelete import TagChangesItemDelete
        from netbluemind.tag.api.TagChangesItemDelete import __TagChangesItemDeleteSerDer__
        deleteValue = value.delete
        instance["delete"] = serder.ListSerDer(__TagChangesItemDeleteSerDer__()).encode(deleteValue)
        return instance

