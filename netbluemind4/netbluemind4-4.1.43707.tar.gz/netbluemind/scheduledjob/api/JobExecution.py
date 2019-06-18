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

class JobExecution :
    def __init__( self):
        self.startDate = None
        self.endDate = None
        self.domainName = None
        self.status = None
        self.jobId = None
        self.execGroup = None
        self.id = None
        pass

class __JobExecutionSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = JobExecution()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        startDateValue = value['startDate']
        instance.startDate = serder.DATE.parse(startDateValue)
        endDateValue = value['endDate']
        instance.endDate = serder.DATE.parse(endDateValue)
        domainNameValue = value['domainName']
        instance.domainName = serder.STRING.parse(domainNameValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusValue = value['status']
        instance.status = __JobExitStatusSerDer__().parse(statusValue)
        jobIdValue = value['jobId']
        instance.jobId = serder.STRING.parse(jobIdValue)
        execGroupValue = value['execGroup']
        instance.execGroup = serder.STRING.parse(execGroupValue)
        idValue = value['id']
        instance.id = serder.INT.parse(idValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        startDateValue = value.startDate
        instance["startDate"] = serder.DATE.encode(startDateValue)
        endDateValue = value.endDate
        instance["endDate"] = serder.DATE.encode(endDateValue)
        domainNameValue = value.domainName
        instance["domainName"] = serder.STRING.encode(domainNameValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusValue = value.status
        instance["status"] = __JobExitStatusSerDer__().encode(statusValue)
        jobIdValue = value.jobId
        instance["jobId"] = serder.STRING.encode(jobIdValue)
        execGroupValue = value.execGroup
        instance["execGroup"] = serder.STRING.encode(execGroupValue)
        idValue = value.id
        instance["id"] = serder.INT.encode(idValue)
        return instance

