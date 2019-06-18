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

class ItemFlagFilter :
    def __init__( self):
        self.must = None
        self.mustNot = None
        pass

class __ItemFlagFilterSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ItemFlagFilter()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.container.model.ItemFlag import ItemFlag
        from netbluemind.core.container.model.ItemFlag import __ItemFlagSerDer__
        mustValue = value['must']
        instance.must = serder.CollectionSerDer(__ItemFlagSerDer__()).parse(mustValue)
        from netbluemind.core.container.model.ItemFlag import ItemFlag
        from netbluemind.core.container.model.ItemFlag import __ItemFlagSerDer__
        mustNotValue = value['mustNot']
        instance.mustNot = serder.CollectionSerDer(__ItemFlagSerDer__()).parse(mustNotValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.container.model.ItemFlag import ItemFlag
        from netbluemind.core.container.model.ItemFlag import __ItemFlagSerDer__
        mustValue = value.must
        instance["must"] = serder.CollectionSerDer(__ItemFlagSerDer__()).encode(mustValue)
        from netbluemind.core.container.model.ItemFlag import ItemFlag
        from netbluemind.core.container.model.ItemFlag import __ItemFlagSerDer__
        mustNotValue = value.mustNot
        instance["mustNot"] = serder.CollectionSerDer(__ItemFlagSerDer__()).encode(mustNotValue)
        return instance

