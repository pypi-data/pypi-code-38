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

IContainers_VERSION = "3.1.41145"

class IContainers(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/containers/_manage'

    def all (self, query ):
        postUri = "/_list";
        __data__ = None
        from netbluemind.core.container.api.ContainerQuery import ContainerQuery
        from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
        __data__ = __ContainerQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
    def getContainers (self, containerIds ):
        postUri = "/_mget";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(containerIds)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
    def setAccessControlList (self, uid , entries ):
        postUri = "/{uid}/_acl";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        __data__ = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(entries)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def update (self, uid , descriptor ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.core.container.model.ContainerModifiableDescriptor import ContainerModifiableDescriptor
        from netbluemind.core.container.model.ContainerModifiableDescriptor import __ContainerModifiableDescriptorSerDer__
        __data__ = __ContainerModifiableDescriptorSerDer__().encode(descriptor)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def allLight (self, query ):
        postUri = "/_listLight";
        __data__ = None
        from netbluemind.core.container.api.ContainerQuery import ContainerQuery
        from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
        __data__ = __ContainerQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.BaseContainerDescriptor import BaseContainerDescriptor
        from netbluemind.core.container.model.BaseContainerDescriptor import __BaseContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__BaseContainerDescriptorSerDer__()), response)
    def allForUser (self, domainUid , userUid , query ):
        postUri = "/_listforuser";
        __data__ = None
        from netbluemind.core.container.api.ContainerQuery import ContainerQuery
        from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
        __data__ = __ContainerQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'domainUid': domainUid  , 'userUid': userUid    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(__ContainerDescriptorSerDer__(), response)
    def create (self, uid , descriptor ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        __data__ = __ContainerDescriptorSerDer__().encode(descriptor)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getIfPresent (self, uid ):
        postUri = "/_ifPresent/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(__ContainerDescriptorSerDer__(), response)
    def getForUser (self, domainUid , userUid , uid ):
        postUri = "/_forUser";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'domainUid': domainUid  , 'userUid': userUid  , 'uid': uid   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainers_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(__ContainerDescriptorSerDer__(), response)
