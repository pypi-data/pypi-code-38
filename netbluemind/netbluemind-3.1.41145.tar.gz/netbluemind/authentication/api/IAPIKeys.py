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

IAPIKeys_VERSION = "3.1.41145"

class IAPIKeys(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/auth/keys'

    def create (self, displayName ):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'displayName': displayName   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAPIKeys_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.APIKey import APIKey
        from netbluemind.authentication.api.APIKey import __APIKeySerDer__
        return self.handleResult__(__APIKeySerDer__(), response)
    def list (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAPIKeys_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.APIKey import APIKey
        from netbluemind.authentication.api.APIKey import __APIKeySerDer__
        return self.handleResult__(serder.ListSerDer(__APIKeySerDer__()), response)
    def delete (self, sid ):
        postUri = "/{sid}";
        __data__ = None
        postUri = postUri.replace("{sid}",sid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAPIKeys_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
