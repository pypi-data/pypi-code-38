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

IComputerTelephonyIntegration_VERSION = "3.1.41145"

class IComputerTelephonyIntegration(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ,userUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/cti/{domainUid}/{userUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)
        self.userUid_ = userUid
        self.base = self.base.replace('{userUid}',userUid)

    def forward (self, component , phoneNumber ):
        postUri = "/forward/{component}";
        __data__ = None
        postUri = postUri.replace("{component}",component);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'phoneNumber': phoneNumber   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IComputerTelephonyIntegration_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getStatus (self):
        postUri = "/status";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IComputerTelephonyIntegration_VERSION}, data = __encoded__);
        from netbluemind.cti.api.Status import Status
        from netbluemind.cti.api.Status import __StatusSerDer__
        return self.handleResult__(__StatusSerDer__(), response)
    def setStatus (self, component , status ):
        postUri = "/status/{component}";
        __data__ = None
        postUri = postUri.replace("{component}",component);
        from netbluemind.cti.api.Status import Status
        from netbluemind.cti.api.Status import __StatusSerDer__
        __data__ = __StatusSerDer__().encode(status)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IComputerTelephonyIntegration_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def dial (self, number ):
        postUri = "/dial";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'number': number   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IComputerTelephonyIntegration_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
