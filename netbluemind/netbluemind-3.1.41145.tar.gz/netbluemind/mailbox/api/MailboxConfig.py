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

class MailboxConfig :
    def __init__( self):
        self.quota = None
        self.messageMaxSize = None
        pass

class __MailboxConfigSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailboxConfig()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        quotaValue = value['quota']
        instance.quota = serder.INT.parse(quotaValue)
        messageMaxSizeValue = value['messageMaxSize']
        instance.messageMaxSize = serder.INT.parse(messageMaxSizeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        quotaValue = value.quota
        instance["quota"] = serder.INT.encode(quotaValue)
        messageMaxSizeValue = value.messageMaxSize
        instance["messageMaxSize"] = serder.INT.encode(messageMaxSizeValue)
        return instance

