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

class VersionInfo :
    def __init__( self):
        self.major = None
        self.minor = None
        self.release = None
        self.displayName = None
        pass

class __VersionInfoSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VersionInfo()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        majorValue = value['major']
        instance.major = serder.STRING.parse(majorValue)
        minorValue = value['minor']
        instance.minor = serder.STRING.parse(minorValue)
        releaseValue = value['release']
        instance.release = serder.STRING.parse(releaseValue)
        displayNameValue = value['displayName']
        instance.displayName = serder.STRING.parse(displayNameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        majorValue = value.major
        instance["major"] = serder.STRING.encode(majorValue)
        minorValue = value.minor
        instance["minor"] = serder.STRING.encode(minorValue)
        releaseValue = value.release
        instance["release"] = serder.STRING.encode(releaseValue)
        displayNameValue = value.displayName
        instance["displayName"] = serder.STRING.encode(displayNameValue)
        return instance

