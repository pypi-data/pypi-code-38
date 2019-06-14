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

IOrgUnits_VERSION = "3.1.41145"

class IOrgUnits(BaseEndpoint):
    def __init__(self, apiKey, url ,domain ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/directory/_ou/{domain}'
        self.domain_ = domain
        self.base = self.base.replace('{domain}',domain)

    def getAdministratorRoles (self, uid , dirUid , groups ):
        postUri = "/{uid}/{dirUid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{dirUid}",dirUid);
        __data__ = serder.ListSerDer(serder.STRING).encode(groups)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def setAdministratorRoles (self, uid , dirUid , roles ):
        postUri = "/{uid}/{dirUid}/_set";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{dirUid}",dirUid);
        __data__ = serder.SetSerDer(serder.STRING).encode(roles)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def update (self, uid , value ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.directory.api.OrgUnit import OrgUnit
        from netbluemind.directory.api.OrgUnit import __OrgUnitSerDer__
        __data__ = __OrgUnitSerDer__().encode(value)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def removeAdministrator (self, administrator ):
        postUri = "/_deleteadmin";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'administrator': administrator   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getAdministrators (self, uid ):
        postUri = "/{uid}/_administrators";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        from netbluemind.directory.api.OrgUnit import OrgUnit
        from netbluemind.directory.api.OrgUnit import __OrgUnitSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__OrgUnitSerDer__()), response)
    def getChildren (self, uid ):
        postUri = "/{uid}/_children";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        from netbluemind.directory.api.OrgUnit import OrgUnit
        from netbluemind.directory.api.OrgUnit import __OrgUnitSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__OrgUnitSerDer__())), response)
    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.directory.api.OrgUnitQuery import OrgUnitQuery
        from netbluemind.directory.api.OrgUnitQuery import __OrgUnitQuerySerDer__
        __data__ = __OrgUnitQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        from netbluemind.directory.api.OrgUnitPath import OrgUnitPath
        from netbluemind.directory.api.OrgUnitPath import __OrgUnitPathSerDer__
        return self.handleResult__(serder.ListSerDer(__OrgUnitPathSerDer__()), response)
    def getPath (self, uid ):
        postUri = "/{uid}/path";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        from netbluemind.directory.api.OrgUnitPath import OrgUnitPath
        from netbluemind.directory.api.OrgUnitPath import __OrgUnitPathSerDer__
        return self.handleResult__(__OrgUnitPathSerDer__(), response)
    def create (self, uid , value ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.directory.api.OrgUnit import OrgUnit
        from netbluemind.directory.api.OrgUnit import __OrgUnitSerDer__
        __data__ = __OrgUnitSerDer__().encode(value)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def listByAdministrator (self, administrator , groups ):
        postUri = "/_byAdmin";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(groups)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'administrator': administrator    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IOrgUnits_VERSION}, data = __encoded__);
        from netbluemind.directory.api.OrgUnitPath import OrgUnitPath
        from netbluemind.directory.api.OrgUnitPath import __OrgUnitPathSerDer__
        return self.handleResult__(serder.ListSerDer(__OrgUnitPathSerDer__()), response)
