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

class DomainTemplateKind :
    def __init__( self):
        self.description = None
        self.tags = None
        self.id = None
        pass

class __DomainTemplateKindSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DomainTemplateKind()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.system.api.DomainTemplateDescription import DomainTemplateDescription
        from netbluemind.system.api.DomainTemplateDescription import __DomainTemplateDescriptionSerDer__
        descriptionValue = value['description']
        instance.description = __DomainTemplateDescriptionSerDer__().parse(descriptionValue)
        from netbluemind.system.api.DomainTemplateTag import DomainTemplateTag
        from netbluemind.system.api.DomainTemplateTag import __DomainTemplateTagSerDer__
        tagsValue = value['tags']
        instance.tags = serder.ListSerDer(__DomainTemplateTagSerDer__()).parse(tagsValue)
        idValue = value['id']
        instance.id = serder.STRING.parse(idValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.system.api.DomainTemplateDescription import DomainTemplateDescription
        from netbluemind.system.api.DomainTemplateDescription import __DomainTemplateDescriptionSerDer__
        descriptionValue = value.description
        instance["description"] = __DomainTemplateDescriptionSerDer__().encode(descriptionValue)
        from netbluemind.system.api.DomainTemplateTag import DomainTemplateTag
        from netbluemind.system.api.DomainTemplateTag import __DomainTemplateTagSerDer__
        tagsValue = value.tags
        instance["tags"] = serder.ListSerDer(__DomainTemplateTagSerDer__()).encode(tagsValue)
        idValue = value.id
        instance["id"] = serder.STRING.encode(idValue)
        return instance

