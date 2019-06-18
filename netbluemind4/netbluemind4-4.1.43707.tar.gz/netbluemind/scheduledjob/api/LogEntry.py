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

class LogEntry :
    def __init__( self):
        self.timestamp = None
        self.severity = None
        self.locale = None
        self.content = None
        self.offset = None
        pass

class __LogEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = LogEntry()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        timestampValue = value['timestamp']
        instance.timestamp = serder.LONG.parse(timestampValue)
        from netbluemind.scheduledjob.api.LogLevel import LogLevel
        from netbluemind.scheduledjob.api.LogLevel import __LogLevelSerDer__
        severityValue = value['severity']
        instance.severity = __LogLevelSerDer__().parse(severityValue)
        localeValue = value['locale']
        instance.locale = serder.STRING.parse(localeValue)
        contentValue = value['content']
        instance.content = serder.STRING.parse(contentValue)
        offsetValue = value['offset']
        instance.offset = serder.INT.parse(offsetValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        timestampValue = value.timestamp
        instance["timestamp"] = serder.LONG.encode(timestampValue)
        from netbluemind.scheduledjob.api.LogLevel import LogLevel
        from netbluemind.scheduledjob.api.LogLevel import __LogLevelSerDer__
        severityValue = value.severity
        instance["severity"] = __LogLevelSerDer__().encode(severityValue)
        localeValue = value.locale
        instance["locale"] = serder.STRING.encode(localeValue)
        contentValue = value.content
        instance["content"] = serder.STRING.encode(contentValue)
        offsetValue = value.offset
        instance["offset"] = serder.INT.encode(offsetValue)
        return instance

