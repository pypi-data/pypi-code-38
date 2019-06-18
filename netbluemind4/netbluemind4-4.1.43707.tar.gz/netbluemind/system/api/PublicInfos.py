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

class PublicInfos :
    def __init__( self):
        self.defaultDomain = None
        self.softwareVersion = None
        self.releaseName = None
        pass

class __PublicInfosSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = PublicInfos()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        defaultDomainValue = value['defaultDomain']
        instance.defaultDomain = serder.STRING.parse(defaultDomainValue)
        softwareVersionValue = value['softwareVersion']
        instance.softwareVersion = serder.STRING.parse(softwareVersionValue)
        releaseNameValue = value['releaseName']
        instance.releaseName = serder.STRING.parse(releaseNameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        defaultDomainValue = value.defaultDomain
        instance["defaultDomain"] = serder.STRING.encode(defaultDomainValue)
        softwareVersionValue = value.softwareVersion
        instance["softwareVersion"] = serder.STRING.encode(softwareVersionValue)
        releaseNameValue = value.releaseName
        instance["releaseName"] = serder.STRING.encode(releaseNameValue)
        return instance

