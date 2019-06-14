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

IResources_VERSION = "3.1.41145"

class IResources(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/resources/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def update (self, uid , rd ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
        from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
        __data__ = __ResourceDescriptorSerDer__().encode(rd)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getIcon (self, uid ):
        postUri = "/{uid}/icon";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def setIcon (self, uid , icon ):
        postUri = "/{uid}/icon";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.ByteArraySerDer.encode(icon)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
        from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
        return self.handleResult__(__ResourceDescriptorSerDer__(), response)
    def byEmail (self, email ):
        postUri = "/byEmail/{email}";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
        from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__ResourceDescriptorSerDer__()), response)
    def create (self, uid , rd ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
        from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
        __data__ = __ResourceDescriptorSerDer__().encode(rd)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byType (self, type ):
        postUri = "/byType/{type}";
        __data__ = None
        postUri = postUri.replace("{type}",type);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IResources_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
