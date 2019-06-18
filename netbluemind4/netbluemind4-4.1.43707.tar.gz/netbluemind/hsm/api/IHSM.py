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

IHSM_VERSION = "4.1.43707"

class IHSM(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/hsm/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def promoteMultiple (self, promote ):
        postUri = "/_massPromote";
        __data__ = None
        __encoded__ = None
        from netbluemind.hsm.api.Promote import Promote
        from netbluemind.hsm.api.Promote import __PromoteSerDer__
        __data__ = serder.ListSerDer(__PromoteSerDer__()).encode(promote)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHSM_VERSION}, data = __encoded__);
        from netbluemind.hsm.api.TierChangeResult import TierChangeResult
        from netbluemind.hsm.api.TierChangeResult import __TierChangeResultSerDer__
        return self.handleResult__(serder.ListSerDer(__TierChangeResultSerDer__()), response)
    def getSize (self, mailboxUid ):
        postUri = "/_getSize/{mailboxUid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHSM_VERSION}, data = __encoded__);
        return self.handleResult__(serder.DOUBLE, response)
    def fetch (self, mailboxUid , hsmId ):
        postUri = "/_fetch/{mailboxUid}/{hsmId}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        postUri = postUri.replace("{hsmId}",hsmId);
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHSM_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def copy (self, sourceMailboxUid , destMailboxUid , hsmIds ):
        postUri = "/_copy/{sourceMailboxUid}/{destMailboxUid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{sourceMailboxUid}",sourceMailboxUid);
        postUri = postUri.replace("{destMailboxUid}",destMailboxUid);
        __data__ = serder.ListSerDer(serder.STRING).encode(hsmIds)
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHSM_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
