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

IDataProtect_VERSION = "3.1.41145"

class IDataProtect(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/dataprotect'

    def saveAll (self):
        postUri = "/_backup";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getContent (self, partGen ):
        postUri = "/_content/{partGen}";
        __data__ = None
        postUri = postUri.replace("{partGen}",partGen);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def run (self, restoreDefinition ):
        postUri = "/restore";
        __data__ = None
        from netbluemind.dataprotect.api.RestoreDefinition import RestoreDefinition
        from netbluemind.dataprotect.api.RestoreDefinition import __RestoreDefinitionSerDer__
        __data__ = __RestoreDefinitionSerDer__().encode(restoreDefinition)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getRestoreCapabilitiesByTags (self, tags ):
        postUri = "/restore/_capabilities_by_tags";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(tags)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
        from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
        return self.handleResult__(serder.ListSerDer(__RestoreOperationSerDer__()), response)
    def installFromGeneration (self, generationId ):
        postUri = "/_install";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'generationId': generationId   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def forget (self, generationId ):
        postUri = "/generations";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'generationId': generationId   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getRestoreCapabilities (self):
        postUri = "/restore/_capabilities";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
        from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
        return self.handleResult__(serder.ListSerDer(__RestoreOperationSerDer__()), response)
    def getRetentionPolicy (self):
        postUri = "/policy";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.dataprotect.api.RetentionPolicy import RetentionPolicy
        from netbluemind.dataprotect.api.RetentionPolicy import __RetentionPolicySerDer__
        return self.handleResult__(__RetentionPolicySerDer__(), response)
    def updatePolicy (self, rp ):
        postUri = "/policy";
        __data__ = None
        from netbluemind.dataprotect.api.RetentionPolicy import RetentionPolicy
        from netbluemind.dataprotect.api.RetentionPolicy import __RetentionPolicySerDer__
        __data__ = __RetentionPolicySerDer__().encode(rp)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getAvailableGenerations (self):
        postUri = "/generations";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        from netbluemind.dataprotect.api.DataProtectGeneration import DataProtectGeneration
        from netbluemind.dataprotect.api.DataProtectGeneration import __DataProtectGenerationSerDer__
        return self.handleResult__(serder.ListSerDer(__DataProtectGenerationSerDer__()), response)
    def syncWithFilesystem (self):
        postUri = "/_syncfs";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDataProtect_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
