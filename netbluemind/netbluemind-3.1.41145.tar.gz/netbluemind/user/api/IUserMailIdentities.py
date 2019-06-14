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

IUserMailIdentities_VERSION = "3.1.41145"

class IUserMailIdentities(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ,userUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/users/{domainUid}/{userUid}/identity'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)
        self.userUid_ = userUid
        self.base = self.base.replace('{userUid}',userUid)

    def update (self, uid , identity ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.user.api.UserMailIdentity import UserMailIdentity
        from netbluemind.user.api.UserMailIdentity import __UserMailIdentitySerDer__
        __data__ = __UserMailIdentitySerDer__().encode(identity)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def setDefault (self, uid ):
        postUri = "/{uid}/_asdefault";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getAvailableIdentities (self):
        postUri = "/_available";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
        from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
        return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
    def get (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        from netbluemind.user.api.UserMailIdentity import UserMailIdentity
        from netbluemind.user.api.UserMailIdentity import __UserMailIdentitySerDer__
        return self.handleResult__(__UserMailIdentitySerDer__(), response)
    def create (self, uid , identity ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.user.api.UserMailIdentity import UserMailIdentity
        from netbluemind.user.api.UserMailIdentity import __UserMailIdentitySerDer__
        __data__ = __UserMailIdentitySerDer__().encode(identity)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getIdentities (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserMailIdentities_VERSION}, data = __encoded__);
        from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
        from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
        return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
