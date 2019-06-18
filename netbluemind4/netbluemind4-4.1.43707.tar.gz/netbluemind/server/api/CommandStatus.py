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

class CommandStatus :
    def __init__( self):
        self.complete = None
        self.successful = None
        self.output = None
        pass

class __CommandStatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = CommandStatus()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        completeValue = value['complete']
        instance.complete = serder.BOOLEAN.parse(completeValue)
        successfulValue = value['successful']
        instance.successful = serder.BOOLEAN.parse(successfulValue)
        outputValue = value['output']
        instance.output = serder.CollectionSerDer(serder.STRING).parse(outputValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        completeValue = value.complete
        instance["complete"] = serder.BOOLEAN.encode(completeValue)
        successfulValue = value.successful
        instance["successful"] = serder.BOOLEAN.encode(successfulValue)
        outputValue = value.output
        instance["output"] = serder.CollectionSerDer(serder.STRING).encode(outputValue)
        return instance

