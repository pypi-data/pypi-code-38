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

class DomainTemplateDescription :
    def __init__( self):
        self.i18n = None
        pass

class __DomainTemplateDescriptionSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DomainTemplateDescription()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.system.api.DomainTemplateDescriptionI18NDescription import DomainTemplateDescriptionI18NDescription
        from netbluemind.system.api.DomainTemplateDescriptionI18NDescription import __DomainTemplateDescriptionI18NDescriptionSerDer__
        i18nValue = value['i18n']
        instance.i18n = serder.ListSerDer(__DomainTemplateDescriptionI18NDescriptionSerDer__()).parse(i18nValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.system.api.DomainTemplateDescriptionI18NDescription import DomainTemplateDescriptionI18NDescription
        from netbluemind.system.api.DomainTemplateDescriptionI18NDescription import __DomainTemplateDescriptionI18NDescriptionSerDer__
        i18nValue = value.i18n
        instance["i18n"] = serder.ListSerDer(__DomainTemplateDescriptionI18NDescriptionSerDer__()).encode(i18nValue)
        return instance

