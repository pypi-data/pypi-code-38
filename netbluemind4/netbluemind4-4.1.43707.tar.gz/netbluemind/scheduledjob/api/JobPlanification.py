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

class JobPlanification :
    def __init__( self):
        self.kind = None
        self.rec = None
        self.lastRun = None
        self.nextRun = None
        self.domain = None
        pass

class __JobPlanificationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = JobPlanification()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.scheduledjob.api.PlanKind import PlanKind
        from netbluemind.scheduledjob.api.PlanKind import __PlanKindSerDer__
        kindValue = value['kind']
        instance.kind = __PlanKindSerDer__().parse(kindValue)
        from netbluemind.scheduledjob.api.JobRec import JobRec
        from netbluemind.scheduledjob.api.JobRec import __JobRecSerDer__
        recValue = value['rec']
        instance.rec = __JobRecSerDer__().parse(recValue)
        lastRunValue = value['lastRun']
        instance.lastRun = serder.DATE.parse(lastRunValue)
        nextRunValue = value['nextRun']
        instance.nextRun = serder.DATE.parse(nextRunValue)
        domainValue = value['domain']
        instance.domain = serder.STRING.parse(domainValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.scheduledjob.api.PlanKind import PlanKind
        from netbluemind.scheduledjob.api.PlanKind import __PlanKindSerDer__
        kindValue = value.kind
        instance["kind"] = __PlanKindSerDer__().encode(kindValue)
        from netbluemind.scheduledjob.api.JobRec import JobRec
        from netbluemind.scheduledjob.api.JobRec import __JobRecSerDer__
        recValue = value.rec
        instance["rec"] = __JobRecSerDer__().encode(recValue)
        lastRunValue = value.lastRun
        instance["lastRun"] = serder.DATE.encode(lastRunValue)
        nextRunValue = value.nextRun
        instance["nextRun"] = serder.DATE.encode(nextRunValue)
        domainValue = value.domain
        instance["domain"] = serder.STRING.encode(domainValue)
        return instance

