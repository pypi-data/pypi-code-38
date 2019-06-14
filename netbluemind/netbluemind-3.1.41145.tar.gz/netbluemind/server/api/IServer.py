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

IServer_VERSION = "3.1.41145"

class IServer(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/servers/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)

    def submit (self, uid , command ):
        postUri = "/{uid}/submit_command";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.STRING.encode(command)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(serder.STRING, response)
    def update (self, uid , srv ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        __data__ = __ServerSerDer__().encode(srv)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getAssignments (self, domainUid ):
        postUri = "/{domainUid}/assignments";
        __data__ = None
        postUri = postUri.replace("{domainUid}",domainUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.Assignment import Assignment
        from netbluemind.server.api.Assignment import __AssignmentSerDer__
        return self.handleResult__(serder.ListSerDer(__AssignmentSerDer__()), response)
    def setTags (self, uid , tags ):
        postUri = "/{uid}/tags";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.ListSerDer(serder.STRING).encode(tags)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getStatus (self, uid , ref ):
        postUri = "/{uid}/command_status";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'ref': ref   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.CommandStatus import CommandStatus
        from netbluemind.server.api.CommandStatus import __CommandStatusSerDer__
        return self.handleResult__(__CommandStatusSerDer__(), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byAssignment (self, domainUid , tag ):
        postUri = "/{domainUid}/byAssignment";
        __data__ = None
        postUri = postUri.replace("{domainUid}",domainUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'tag': tag   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def create (self, uid , srv ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        __data__ = __ServerSerDer__().encode(srv)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def allComplete (self):
        postUri = "/_complete";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__ServerSerDer__())), response)
    def writeFile (self, uid , path , content ):
        postUri = "/{uid}/fs/{path}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{path}",path);
        __data__ = serder.ByteArraySerDer.encode(content)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def unassign (self, serverUid , domainUid , tag ):
        postUri = "/{domainUid}/assignments/{serverUid}/_unassign";
        __data__ = None
        postUri = postUri.replace("{serverUid}",serverUid);
        postUri = postUri.replace("{domainUid}",domainUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    'tag': tag   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__ServerSerDer__()), response)
    def getServerAssignments (self, uid ):
        postUri = "/{uid}/serverAssignments";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.Assignment import Assignment
        from netbluemind.server.api.Assignment import __AssignmentSerDer__
        return self.handleResult__(serder.ListSerDer(__AssignmentSerDer__()), response)
    def readFile (self, uid , path ):
        postUri = "/{uid}/fs/{path}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def submitAndWait (self, uid , command ):
        postUri = "/{uid}/submit_command_and_wait";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.STRING.encode(command)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        from netbluemind.server.api.CommandStatus import CommandStatus
        from netbluemind.server.api.CommandStatus import __CommandStatusSerDer__
        return self.handleResult__(__CommandStatusSerDer__(), response)
    def assign (self, serverUid , domainUid , tag ):
        postUri = "/{domainUid}/assignments/{serverUid}/_assign";
        __data__ = None
        postUri = postUri.replace("{serverUid}",serverUid);
        postUri = postUri.replace("{domainUid}",domainUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    'tag': tag   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IServer_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
