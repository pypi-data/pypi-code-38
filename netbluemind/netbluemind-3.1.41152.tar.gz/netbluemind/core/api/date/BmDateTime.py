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

class BmDateTime :
    def __init__( self):
        self.iso8601 = None
        self.timezone = None
        self.precision = None
        pass

class __BmDateTimeSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = BmDateTime()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        iso8601Value = value['iso8601']
        instance.iso8601 = serder.STRING.parse(iso8601Value)
        timezoneValue = value['timezone']
        instance.timezone = serder.STRING.parse(timezoneValue)
        from netbluemind.core.api.date.BmDateTimePrecision import BmDateTimePrecision
        from netbluemind.core.api.date.BmDateTimePrecision import __BmDateTimePrecisionSerDer__
        precisionValue = value['precision']
        instance.precision = __BmDateTimePrecisionSerDer__().parse(precisionValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        iso8601Value = value.iso8601
        instance["iso8601"] = serder.STRING.encode(iso8601Value)
        timezoneValue = value.timezone
        instance["timezone"] = serder.STRING.encode(timezoneValue)
        from netbluemind.core.api.date.BmDateTimePrecision import BmDateTimePrecision
        from netbluemind.core.api.date.BmDateTimePrecision import __BmDateTimePrecisionSerDer__
        precisionValue = value.precision
        instance["precision"] = __BmDateTimePrecisionSerDer__().encode(precisionValue)
        return instance

