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

class PartGeneration :
    def __init__( self):
        self.id = None
        self.generationId = None
        self.begin = None
        self.end = None
        self.size = None
        self.tag = None
        self.server = None
        self.withWarnings = None
        self.withErrors = None
        self.valid = None
        pass

class __PartGenerationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = PartGeneration()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.INT.parse(idValue)
        generationIdValue = value['generationId']
        instance.generationId = serder.INT.parse(generationIdValue)
        beginValue = value['begin']
        instance.begin = serder.DATE.parse(beginValue)
        endValue = value['end']
        instance.end = serder.DATE.parse(endValue)
        sizeValue = value['size']
        instance.size = serder.LONG.parse(sizeValue)
        tagValue = value['tag']
        instance.tag = serder.STRING.parse(tagValue)
        serverValue = value['server']
        instance.server = serder.STRING.parse(serverValue)
        withWarningsValue = value['withWarnings']
        instance.withWarnings = serder.BOOLEAN.parse(withWarningsValue)
        withErrorsValue = value['withErrors']
        instance.withErrors = serder.BOOLEAN.parse(withErrorsValue)
        from netbluemind.dataprotect.api.GenerationStatus import GenerationStatus
        from netbluemind.dataprotect.api.GenerationStatus import __GenerationStatusSerDer__
        validValue = value['valid']
        instance.valid = __GenerationStatusSerDer__().parse(validValue)
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
        generationIdValue = value.generationId
        instance["generationId"] = serder.INT.encode(generationIdValue)
        beginValue = value.begin
        instance["begin"] = serder.DATE.encode(beginValue)
        endValue = value.end
        instance["end"] = serder.DATE.encode(endValue)
        sizeValue = value.size
        instance["size"] = serder.LONG.encode(sizeValue)
        tagValue = value.tag
        instance["tag"] = serder.STRING.encode(tagValue)
        serverValue = value.server
        instance["server"] = serder.STRING.encode(serverValue)
        withWarningsValue = value.withWarnings
        instance["withWarnings"] = serder.BOOLEAN.encode(withWarningsValue)
        withErrorsValue = value.withErrors
        instance["withErrors"] = serder.BOOLEAN.encode(withErrorsValue)
        from netbluemind.dataprotect.api.GenerationStatus import GenerationStatus
        from netbluemind.dataprotect.api.GenerationStatus import __GenerationStatusSerDer__
        validValue = value.valid
        instance["valid"] = __GenerationStatusSerDer__().encode(validValue)
        return instance

