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

IPublishCalendar_VERSION = "4.1.43707"

class IPublishCalendar(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/calendars/publish/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)

    def generateUrl (self, mode ):
        postUri = "/_generate/{mode}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mode}",mode);
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublishCalendar_VERSION}, data = __encoded__);
        return self.handleResult__(serder.STRING, response)
    def disableUrl (self, url ):
        postUri = "/_disable";
        __data__ = None
        __encoded__ = None
        __data__ = serder.STRING.encode(url)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublishCalendar_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getGeneratedUrls (self, mode ):
        postUri = "/generated/{mode}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mode}",mode);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublishCalendar_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def publish (self, token ):
        postUri = "/{token}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{token}",token);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IPublishCalendar_VERSION}, data = __encoded__);
        return response.content
