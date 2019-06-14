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

class JobExecutionQuery :
    def __init__( self):
        self.jobId = None
        self.domain = None
        self.id = None
        self.statuses = None
        self.active = None
        self.from_ = None
        self.size = None
        pass

class __JobExecutionQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = JobExecutionQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        jobIdValue = value['jobId']
        instance.jobId = serder.STRING.parse(jobIdValue)
        domainValue = value['domain']
        instance.domain = serder.STRING.parse(domainValue)
        idValue = value['id']
        instance.id = serder.INT.parse(idValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusesValue = value['statuses']
        instance.statuses = serder.SetSerDer(__JobExitStatusSerDer__()).parse(statusesValue)
        activeValue = value['active']
        instance.active = serder.BOOLEAN.parse(activeValue)
        from_Value = value['from']
        instance.from_ = serder.INT.parse(from_Value)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        jobIdValue = value.jobId
        instance["jobId"] = serder.STRING.encode(jobIdValue)
        domainValue = value.domain
        instance["domain"] = serder.STRING.encode(domainValue)
        idValue = value.id
        instance["id"] = serder.INT.encode(idValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusesValue = value.statuses
        instance["statuses"] = serder.SetSerDer(__JobExitStatusSerDer__()).encode(statusesValue)
        activeValue = value.active
        instance["active"] = serder.BOOLEAN.encode(activeValue)
        from_Value = value.from_
        instance["from"] = serder.INT.encode(from_Value)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        return instance

