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

IMailboxIdentity_VERSION = "3.1.41145"

class IMailboxIdentity(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ,mboxUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mailboxes/{domainUid}/identity/{mboxUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)
        self.mboxUid_ = mboxUid
        self.base = self.base.replace('{mboxUid}',mboxUid)

    def update (self, uid , identity ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.mailbox.identity.api.Identity import Identity
        from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
        __data__ = __IdentitySerDer__().encode(identity)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        from netbluemind.mailbox.identity.api.Identity import Identity
        from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
        return self.handleResult__(__IdentitySerDer__(), response)
    def getPossibleIdentities (self):
        postUri = "/_possible";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
        from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
        return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
    def create (self, uid , identity ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.mailbox.identity.api.Identity import Identity
        from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
        __data__ = __IdentitySerDer__().encode(identity)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getIdentities (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxIdentity_VERSION}, data = __encoded__);
        from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
        from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
        return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
