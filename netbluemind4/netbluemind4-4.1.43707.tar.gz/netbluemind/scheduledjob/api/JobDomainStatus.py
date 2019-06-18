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

class JobDomainStatus :
    def __init__( self):
        self.domain = None
        self.status = None
        pass

class __JobDomainStatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = JobDomainStatus()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        domainValue = value['domain']
        instance.domain = serder.STRING.parse(domainValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusValue = value['status']
        instance.status = __JobExitStatusSerDer__().parse(statusValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        domainValue = value.domain
        instance["domain"] = serder.STRING.encode(domainValue)
        from netbluemind.scheduledjob.api.JobExitStatus import JobExitStatus
        from netbluemind.scheduledjob.api.JobExitStatus import __JobExitStatusSerDer__
        statusValue = value.status
        instance["status"] = __JobExitStatusSerDer__().encode(statusValue)
        return instance

