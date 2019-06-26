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

class Job :
    def __init__( self):
        self.domainStatus = None
        self.domainPlanification = None
        self.id = None
        self.description = None
        self.kind = None
        self.sendReport = None
        self.recipients = None
        pass

class __JobSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Job()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.scheduledjob.api.JobDomainStatus import JobDomainStatus
        from netbluemind.scheduledjob.api.JobDomainStatus import __JobDomainStatusSerDer__
        domainStatusValue = value['domainStatus']
        instance.domainStatus = serder.ListSerDer(__JobDomainStatusSerDer__()).parse(domainStatusValue)
        from netbluemind.scheduledjob.api.JobPlanification import JobPlanification
        from netbluemind.scheduledjob.api.JobPlanification import __JobPlanificationSerDer__
        domainPlanificationValue = value['domainPlanification']
        instance.domainPlanification = serder.ListSerDer(__JobPlanificationSerDer__()).parse(domainPlanificationValue)
        idValue = value['id']
        instance.id = serder.STRING.parse(idValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        from netbluemind.scheduledjob.api.JobKind import JobKind
        from netbluemind.scheduledjob.api.JobKind import __JobKindSerDer__
        kindValue = value['kind']
        instance.kind = __JobKindSerDer__().parse(kindValue)
        sendReportValue = value['sendReport']
        instance.sendReport = serder.BOOLEAN.parse(sendReportValue)
        recipientsValue = value['recipients']
        instance.recipients = serder.STRING.parse(recipientsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.scheduledjob.api.JobDomainStatus import JobDomainStatus
        from netbluemind.scheduledjob.api.JobDomainStatus import __JobDomainStatusSerDer__
        domainStatusValue = value.domainStatus
        instance["domainStatus"] = serder.ListSerDer(__JobDomainStatusSerDer__()).encode(domainStatusValue)
        from netbluemind.scheduledjob.api.JobPlanification import JobPlanification
        from netbluemind.scheduledjob.api.JobPlanification import __JobPlanificationSerDer__
        domainPlanificationValue = value.domainPlanification
        instance["domainPlanification"] = serder.ListSerDer(__JobPlanificationSerDer__()).encode(domainPlanificationValue)
        idValue = value.id
        instance["id"] = serder.STRING.encode(idValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        from netbluemind.scheduledjob.api.JobKind import JobKind
        from netbluemind.scheduledjob.api.JobKind import __JobKindSerDer__
        kindValue = value.kind
        instance["kind"] = __JobKindSerDer__().encode(kindValue)
        sendReportValue = value.sendReport
        instance["sendReport"] = serder.BOOLEAN.encode(sendReportValue)
        recipientsValue = value.recipients
        instance["recipients"] = serder.STRING.encode(recipientsValue)
        return instance

