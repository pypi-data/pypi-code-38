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

class RetentionPolicy :
    def __init__( self):
        self.daily = None
        self.weekly = None
        self.monthly = None
        pass

class __RetentionPolicySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = RetentionPolicy()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        dailyValue = value['daily']
        instance.daily = serder.INT.parse(dailyValue)
        weeklyValue = value['weekly']
        instance.weekly = serder.INT.parse(weeklyValue)
        monthlyValue = value['monthly']
        instance.monthly = serder.INT.parse(monthlyValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        dailyValue = value.daily
        instance["daily"] = serder.INT.encode(dailyValue)
        weeklyValue = value.weekly
        instance["weekly"] = serder.INT.encode(weeklyValue)
        monthlyValue = value.monthly
        instance["monthly"] = serder.INT.encode(monthlyValue)
        return instance

