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

class FileHostingPublicLink :
    def __init__( self):
        self.url = None
        self.expirationDate = None
        pass

class __FileHostingPublicLinkSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = FileHostingPublicLink()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        urlValue = value['url']
        instance.url = serder.STRING.parse(urlValue)
        expirationDateValue = value['expirationDate']
        instance.expirationDate = serder.LONG.parse(expirationDateValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        urlValue = value.url
        instance["url"] = serder.STRING.encode(urlValue)
        expirationDateValue = value.expirationDate
        instance["expirationDate"] = serder.LONG.encode(expirationDateValue)
        return instance

