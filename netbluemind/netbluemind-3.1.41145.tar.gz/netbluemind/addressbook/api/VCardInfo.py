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

class VCardInfo :
    def __init__( self):
        self.kind = None
        self.mail = None
        self.tel = None
        self.formatedName = None
        self.categories = None
        self.memberCount = None
        self.photo = None
        self.source = None
        pass

class __VCardInfoSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardInfo()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardKind import VCardKind
        from netbluemind.addressbook.api.VCardKind import __VCardKindSerDer__
        kindValue = value['kind']
        instance.kind = __VCardKindSerDer__().parse(kindValue)
        mailValue = value['mail']
        instance.mail = serder.STRING.parse(mailValue)
        telValue = value['tel']
        instance.tel = serder.STRING.parse(telValue)
        formatedNameValue = value['formatedName']
        instance.formatedName = serder.STRING.parse(formatedNameValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value['categories']
        instance.categories = serder.ListSerDer(__TagRefSerDer__()).parse(categoriesValue)
        memberCountValue = value['memberCount']
        instance.memberCount = serder.INT.parse(memberCountValue)
        photoValue = value['photo']
        instance.photo = serder.BOOLEAN.parse(photoValue)
        sourceValue = value['source']
        instance.source = serder.STRING.parse(sourceValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardKind import VCardKind
        from netbluemind.addressbook.api.VCardKind import __VCardKindSerDer__
        kindValue = value.kind
        instance["kind"] = __VCardKindSerDer__().encode(kindValue)
        mailValue = value.mail
        instance["mail"] = serder.STRING.encode(mailValue)
        telValue = value.tel
        instance["tel"] = serder.STRING.encode(telValue)
        formatedNameValue = value.formatedName
        instance["formatedName"] = serder.STRING.encode(formatedNameValue)
        from netbluemind.tag.api.TagRef import TagRef
        from netbluemind.tag.api.TagRef import __TagRefSerDer__
        categoriesValue = value.categories
        instance["categories"] = serder.ListSerDer(__TagRefSerDer__()).encode(categoriesValue)
        memberCountValue = value.memberCount
        instance["memberCount"] = serder.INT.encode(memberCountValue)
        photoValue = value.photo
        instance["photo"] = serder.BOOLEAN.encode(photoValue)
        sourceValue = value.source
        instance["source"] = serder.STRING.encode(sourceValue)
        return instance

