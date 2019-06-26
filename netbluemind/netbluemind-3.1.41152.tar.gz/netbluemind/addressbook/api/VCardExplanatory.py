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

class VCardExplanatory :
    def __init__( self):
        self.urls = None
        self.categories = None
        self.note = None
        pass

class __VCardExplanatorySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardExplanatory()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardExplanatoryUrl import VCardExplanatoryUrl
        from netbluemind.addressbook.api.VCardExplanatoryUrl import __VCardExplanatoryUrlSerDer__
        urlsValue = value['urls']
        instance.urls = serder.ListSerDer(__VCardExplanatoryUrlSerDer__()).parse(urlsValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value['categories']
        instance.categories = serder.ListSerDer(__TagRefSerDer__()).parse(categoriesValue)
        noteValue = value['note']
        instance.note = serder.STRING.parse(noteValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardExplanatoryUrl import VCardExplanatoryUrl
        from netbluemind.addressbook.api.VCardExplanatoryUrl import __VCardExplanatoryUrlSerDer__
        urlsValue = value.urls
        instance["urls"] = serder.ListSerDer(__VCardExplanatoryUrlSerDer__()).encode(urlsValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value.categories
        instance["categories"] = serder.ListSerDer(__TagRefSerDer__()).encode(categoriesValue)
        noteValue = value.note
        instance["note"] = serder.STRING.encode(noteValue)
        return instance

