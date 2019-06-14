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

IContainerManagement_VERSION = "3.1.41145"

class IContainerManagement(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/containers/_manage/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)

    def getDescriptor (self):
        postUri = "/_descriptor";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(__ContainerDescriptorSerDer__(), response)
    def getSettings (self):
        postUri = "/_settings";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(serder.MapSerDer(serder.STRING), response)
    def getAccessControlList (self):
        postUri = "/_acl";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        return self.handleResult__(serder.ListSerDer(__AccessControlEntrySerDer__()), response)
    def getAllItems (self):
        postUri = "/_list";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemDescriptor import ItemDescriptor
        from netbluemind.core.container.model.ItemDescriptor import __ItemDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemDescriptorSerDer__()), response)
    def subscribers (self):
        postUri = "/_subscription";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def getItemCount (self):
        postUri = "/_itemCount";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Count import Count
        from netbluemind.core.container.api.Count import __CountSerDer__
        return self.handleResult__(__CountSerDer__(), response)
    def setAccessControlList (self, entries ):
        postUri = "/_acl";
        __data__ = None
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        __data__ = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(entries)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def update (self, descriptor ):
        postUri = "/_descriptor";
        __data__ = None
        from netbluemind.core.container.model.ContainerModifiableDescriptor import ContainerModifiableDescriptor
        from netbluemind.core.container.model.ContainerModifiableDescriptor import __ContainerModifiableDescriptorSerDer__
        __data__ = __ContainerModifiableDescriptorSerDer__().encode(descriptor)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def allowOfflineSync (self, subject ):
        postUri = "/{subject}/offlineSync";
        __data__ = None
        postUri = postUri.replace("{subject}",subject);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def setSettings (self, settings ):
        postUri = "/_settings";
        __data__ = None
        __data__ = serder.MapSerDer(serder.STRING).encode(settings)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getItems (self, uids ):
        postUri = "/_mget";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemDescriptor import ItemDescriptor
        from netbluemind.core.container.model.ItemDescriptor import __ItemDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemDescriptorSerDer__()), response)
    def disallowOfflineSync (self, subject ):
        postUri = "/{subject}/offlineSync";
        __data__ = None
        postUri = postUri.replace("{subject}",subject);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def setPersonalSettings (self, settings ):
        postUri = "/_personalSettings";
        __data__ = None
        __data__ = serder.MapSerDer(serder.STRING).encode(settings)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IContainerManagement_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
