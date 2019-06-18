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

class ICalendarElementOrganizer :
    def __init__( self):
        self.uri = None
        self.commonName = None
        self.mailto = None
        self.dir = None
        pass

class __ICalendarElementOrganizerSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ICalendarElementOrganizer()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        uriValue = value['uri']
        instance.uri = serder.STRING.parse(uriValue)
        commonNameValue = value['commonName']
        instance.commonName = serder.STRING.parse(commonNameValue)
        mailtoValue = value['mailto']
        instance.mailto = serder.STRING.parse(mailtoValue)
        dirValue = value['dir']
        instance.dir = serder.STRING.parse(dirValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        uriValue = value.uri
        instance["uri"] = serder.STRING.encode(uriValue)
        commonNameValue = value.commonName
        instance["commonName"] = serder.STRING.encode(commonNameValue)
        mailtoValue = value.mailto
        instance["mailto"] = serder.STRING.encode(mailtoValue)
        dirValue = value.dir
        instance["dir"] = serder.STRING.encode(dirValue)
        return instance

