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

class TaskStatus :
    def __init__( self):
        self.steps = None
        self.progress = None
        self.lastLogEntry = None
        self.state = None
        self.result = None
        pass

class __TaskStatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = TaskStatus()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        stepsValue = value['steps']
        instance.steps = serder.DOUBLE.parse(stepsValue)
        progressValue = value['progress']
        instance.progress = serder.DOUBLE.parse(progressValue)
        lastLogEntryValue = value['lastLogEntry']
        instance.lastLogEntry = serder.STRING.parse(lastLogEntryValue)
        from netbluemind.core.task.api.TaskStatusState import TaskStatusState
        from netbluemind.core.task.api.TaskStatusState import __TaskStatusStateSerDer__
        stateValue = value['state']
        instance.state = __TaskStatusStateSerDer__().parse(stateValue)
        resultValue = value['result']
        instance.result = serder.STRING.parse(resultValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        stepsValue = value.steps
        instance["steps"] = serder.DOUBLE.encode(stepsValue)
        progressValue = value.progress
        instance["progress"] = serder.DOUBLE.encode(progressValue)
        lastLogEntryValue = value.lastLogEntry
        instance["lastLogEntry"] = serder.STRING.encode(lastLogEntryValue)
        from netbluemind.core.task.api.TaskStatusState import TaskStatusState
        from netbluemind.core.task.api.TaskStatusState import __TaskStatusStateSerDer__
        stateValue = value.state
        instance["state"] = __TaskStatusStateSerDer__().encode(stateValue)
        resultValue = value.result
        instance["result"] = serder.STRING.encode(resultValue)
        return instance

