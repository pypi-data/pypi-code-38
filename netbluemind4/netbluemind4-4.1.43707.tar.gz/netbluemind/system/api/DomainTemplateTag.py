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

class DomainTemplateTag :
    def __init__( self):
        self.value = None
        self.description = None
        self.multival = None
        self.mandatory = None
        self.autoAssign = None
        pass

class __DomainTemplateTagSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DomainTemplateTag()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        valueValue = value['value']
        instance.value = serder.STRING.parse(valueValue)
        from netbluemind.system.api.DomainTemplateDescription import DomainTemplateDescription
        from netbluemind.system.api.DomainTemplateDescription import __DomainTemplateDescriptionSerDer__
        descriptionValue = value['description']
        instance.description = __DomainTemplateDescriptionSerDer__().parse(descriptionValue)
        multivalValue = value['multival']
        instance.multival = serder.BOOLEAN.parse(multivalValue)
        mandatoryValue = value['mandatory']
        instance.mandatory = serder.BOOLEAN.parse(mandatoryValue)
        autoAssignValue = value['autoAssign']
        instance.autoAssign = serder.BOOLEAN.parse(autoAssignValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        valueValue = value.value
        instance["value"] = serder.STRING.encode(valueValue)
        from netbluemind.system.api.DomainTemplateDescription import DomainTemplateDescription
        from netbluemind.system.api.DomainTemplateDescription import __DomainTemplateDescriptionSerDer__
        descriptionValue = value.description
        instance["description"] = __DomainTemplateDescriptionSerDer__().encode(descriptionValue)
        multivalValue = value.multival
        instance["multival"] = serder.BOOLEAN.encode(multivalValue)
        mandatoryValue = value.mandatory
        instance["mandatory"] = serder.BOOLEAN.encode(mandatoryValue)
        autoAssignValue = value.autoAssign
        instance["autoAssign"] = serder.BOOLEAN.encode(autoAssignValue)
        return instance

