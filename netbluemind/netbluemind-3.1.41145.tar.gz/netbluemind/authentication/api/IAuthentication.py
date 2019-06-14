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

IAuthentication_VERSION = "3.1.41145"

class IAuthentication(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/auth'

    def getCurrentUser (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.AuthUser import AuthUser
        from netbluemind.authentication.api.AuthUser import __AuthUserSerDer__
        return self.handleResult__(__AuthUserSerDer__(), response)
    def su (self, login ):
        postUri = "/_su";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'login': login   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.LoginResponse import LoginResponse
        from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
        return self.handleResult__(__LoginResponseSerDer__(), response)
    def ping (self):
        postUri = "/ping";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def login (self, login , password , origin ):
        postUri = "/login";
        __data__ = None
        __data__ = serder.STRING.encode(password)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'login': login   , 'origin': origin   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.LoginResponse import LoginResponse
        from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
        return self.handleResult__(__LoginResponseSerDer__(), response)
    def loginWithParams (self, login , password , origin , interactive ):
        postUri = "/loginWithParams";
        __data__ = None
        __data__ = serder.STRING.encode(password)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'login': login   , 'origin': origin  , 'interactive': interactive   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.LoginResponse import LoginResponse
        from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
        return self.handleResult__(__LoginResponseSerDer__(), response)
    def logout (self):
        postUri = "/logout";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def suWithParams (self, login , interactive ):
        postUri = "/_suWithParams";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'login': login  , 'interactive': interactive   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.LoginResponse import LoginResponse
        from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
        return self.handleResult__(__LoginResponseSerDer__(), response)
    def validate (self, login , password , origin ):
        postUri = "/validate";
        __data__ = None
        __data__ = serder.STRING.encode(password)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'login': login   , 'origin': origin   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAuthentication_VERSION}, data = __encoded__);
        from netbluemind.authentication.api.ValidationKind import ValidationKind
        from netbluemind.authentication.api.ValidationKind import __ValidationKindSerDer__
        return self.handleResult__(__ValidationKindSerDer__(), response)
