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

class SeenUpdate :
    def __init__( self):
        self.itemId = None
        self.seen = None
        self.mdnSent = None
        pass

class __SeenUpdateSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SeenUpdate()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        itemIdValue = value['itemId']
        instance.itemId = serder.LONG.parse(itemIdValue)
        seenValue = value['seen']
        instance.seen = serder.BOOLEAN.parse(seenValue)
        mdnSentValue = value['mdnSent']
        instance.mdnSent = serder.BOOLEAN.parse(mdnSentValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        itemIdValue = value.itemId
        instance["itemId"] = serder.LONG.encode(itemIdValue)
        seenValue = value.seen
        instance["seen"] = serder.BOOLEAN.encode(seenValue)
        mdnSentValue = value.mdnSent
        instance["mdnSent"] = serder.BOOLEAN.encode(mdnSentValue)
        return instance

