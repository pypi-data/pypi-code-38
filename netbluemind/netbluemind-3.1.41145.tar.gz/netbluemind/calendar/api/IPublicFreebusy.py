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
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IPublicFreebusy_VERSION = "3.1.41145"

class IPublicFreebusy(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars/sfreebusy'

    def get (self, email , callerUserUid , callerDomain , query ):
        postUri = "/{email}";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        from netbluemind.calendar.api.VFreebusyQuery import VFreebusyQuery
        from netbluemind.calendar.api.VFreebusyQuery import __VFreebusyQuerySerDer__
        __data__ = __VFreebusyQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'callerUserUid': callerUserUid  , 'callerDomain': callerDomain    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublicFreebusy_VERSION}, data = __encoded__);
        from netbluemind.calendar.api.VFreebusy import VFreebusy
        from netbluemind.calendar.api.VFreebusy import __VFreebusySerDer__
        return self.handleResult__(__VFreebusySerDer__(), response)
    def getAsString (self, email , callerUserUid , callerDomain , query ):
        postUri = "/{email}/_ics";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        from netbluemind.calendar.api.VFreebusyQuery import VFreebusyQuery
        from netbluemind.calendar.api.VFreebusyQuery import __VFreebusyQuerySerDer__
        __data__ = __VFreebusyQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'callerUserUid': callerUserUid  , 'callerDomain': callerDomain    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublicFreebusy_VERSION}, data = __encoded__);
        return self.handleResult__(serder.STRING, response)
    def simple (self, email , callerUserUid , callerDomain ):
        postUri = "/{email}";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'callerUserUid': callerUserUid  , 'callerDomain': callerDomain   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublicFreebusy_VERSION}, data = __encoded__);
        return self.handleResult__(serder.STRING, response)
