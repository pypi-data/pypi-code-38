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

class DataProtectGeneration :
    def __init__( self):
        self.id = None
        self.protectionTime = None
        self.blueMind = None
        self.withWarnings = None
        self.withErrors = None
        self.parts = None
        pass

class __DataProtectGenerationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DataProtectGeneration()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.INT.parse(idValue)
        protectionTimeValue = value['protectionTime']
        instance.protectionTime = serder.DATE.parse(protectionTimeValue)
        from netbluemind.core.api.VersionInfo import VersionInfo
        from netbluemind.core.api.VersionInfo import __VersionInfoSerDer__
        blueMindValue = value['blueMind']
        instance.blueMind = __VersionInfoSerDer__().parse(blueMindValue)
        withWarningsValue = value['withWarnings']
        instance.withWarnings = serder.BOOLEAN.parse(withWarningsValue)
        withErrorsValue = value['withErrors']
        instance.withErrors = serder.BOOLEAN.parse(withErrorsValue)
        from netbluemind.dataprotect.api.PartGeneration import PartGeneration
        from netbluemind.dataprotect.api.PartGeneration import __PartGenerationSerDer__
        partsValue = value['parts']
        instance.parts = serder.ListSerDer(__PartGenerationSerDer__()).parse(partsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        idValue = value.id
        instance["id"] = serder.INT.encode(idValue)
        protectionTimeValue = value.protectionTime
        instance["protectionTime"] = serder.DATE.encode(protectionTimeValue)
        from netbluemind.core.api.VersionInfo import VersionInfo
        from netbluemind.core.api.VersionInfo import __VersionInfoSerDer__
        blueMindValue = value.blueMind
        instance["blueMind"] = __VersionInfoSerDer__().encode(blueMindValue)
        withWarningsValue = value.withWarnings
        instance["withWarnings"] = serder.BOOLEAN.encode(withWarningsValue)
        withErrorsValue = value.withErrors
        instance["withErrors"] = serder.BOOLEAN.encode(withErrorsValue)
        from netbluemind.dataprotect.api.PartGeneration import PartGeneration
        from netbluemind.dataprotect.api.PartGeneration import __PartGenerationSerDer__
        partsValue = value.parts
        instance["parts"] = serder.ListSerDer(__PartGenerationSerDer__()).encode(partsValue)
        return instance

