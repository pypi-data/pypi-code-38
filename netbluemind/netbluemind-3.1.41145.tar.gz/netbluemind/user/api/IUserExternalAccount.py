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

IUserExternalAccount_VERSION = "3.1.41145"

class IUserExternalAccount(BaseEndpoint):
    def __init__(self, apiKey, url ,domain ,uid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/users/{domain}/{uid}/accounts'
        self.domain_ = domain
        self.base = self.base.replace('{domain}',domain)
        self.uid_ = uid
        self.base = self.base.replace('{uid}',uid)

    def getAll (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        from netbluemind.user.api.UserAccountInfo import UserAccountInfo
        from netbluemind.user.api.UserAccountInfo import __UserAccountInfoSerDer__
        return self.handleResult__(serder.ListSerDer(__UserAccountInfoSerDer__()), response)
    def deleteAll (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def update (self, system , account ):
        postUri = "/{system}";
        __data__ = None
        postUri = postUri.replace("{system}",system);
        from netbluemind.user.api.UserAccount import UserAccount
        from netbluemind.user.api.UserAccount import __UserAccountSerDer__
        __data__ = __UserAccountSerDer__().encode(account)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, system ):
        postUri = "/{system}";
        __data__ = None
        postUri = postUri.replace("{system}",system);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self, system ):
        postUri = "/{system}";
        __data__ = None
        postUri = postUri.replace("{system}",system);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        from netbluemind.user.api.UserAccount import UserAccount
        from netbluemind.user.api.UserAccount import __UserAccountSerDer__
        return self.handleResult__(__UserAccountSerDer__(), response)
    def create (self, system , account ):
        postUri = "/{system}";
        __data__ = None
        postUri = postUri.replace("{system}",system);
        from netbluemind.user.api.UserAccount import UserAccount
        from netbluemind.user.api.UserAccount import __UserAccountSerDer__
        __data__ = __UserAccountSerDer__().encode(account)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserExternalAccount_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
