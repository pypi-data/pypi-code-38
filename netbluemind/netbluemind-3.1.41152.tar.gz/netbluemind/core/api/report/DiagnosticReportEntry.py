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

class DiagnosticReportEntry :
    def __init__( self):
        self.id = None
        self.state = None
        self.message = None
        self.timestamp = None
        self.stack = None
        pass

class __DiagnosticReportEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DiagnosticReportEntry()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.STRING.parse(idValue)
        from netbluemind.core.api.report.DiagnosticReportState import DiagnosticReportState
        from netbluemind.core.api.report.DiagnosticReportState import __DiagnosticReportStateSerDer__
        stateValue = value['state']
        instance.state = __DiagnosticReportStateSerDer__().parse(stateValue)
        messageValue = value['message']
        instance.message = serder.STRING.parse(messageValue)
        timestampValue = value['timestamp']
        instance.timestamp = serder.LONG.parse(timestampValue)
        stackValue = value['stack']
        instance.stack = serder.ArraySerDer(serder.STRING).parse(stackValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        idValue = value.id
        instance["id"] = serder.STRING.encode(idValue)
        from netbluemind.core.api.report.DiagnosticReportState import DiagnosticReportState
        from netbluemind.core.api.report.DiagnosticReportState import __DiagnosticReportStateSerDer__
        stateValue = value.state
        instance["state"] = __DiagnosticReportStateSerDer__().encode(stateValue)
        messageValue = value.message
        instance["message"] = serder.STRING.encode(messageValue)
        timestampValue = value.timestamp
        instance["timestamp"] = serder.LONG.encode(timestampValue)
        stackValue = value.stack
        instance["stack"] = serder.ArraySerDer(serder.STRING).encode(stackValue)
        return instance

