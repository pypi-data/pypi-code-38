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

IMailboxFolderHierarchy_VERSION = "3.1.41145"

class IMailboxFolderHierarchy(BaseEndpoint):
    def __init__(self, apiKey, url ,mailboxUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mailbox-folders/{mailboxUid}'
        self.mailboxUid_ = mailboxUid
        self.base = self.base.replace('{mailboxUid}',mailboxUid)

    def multipleGet (self, arg0 ):
        postUri = "/_mget";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(arg0)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__FolderSerDer__())), response)
    def byUid (self, uid ):
        postUri = "/by_uid";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'uid': uid   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
    def allUids (self):
        postUri = "/_alluids";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def byParentId (self, parent ):
        postUri = "/by_parent_id";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'parent': parent   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__FolderSerDer__())), response)
    def changelog (self, arg0 ):
        postUri = "/_changelog";
        __data__ = None
        __data__ = serder.LONG.encode(arg0)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def changesetById (self, since ):
        postUri = "/_changesetById";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
    def search (self, arg0 ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.folder.api.FolderQuery import FolderQuery
        from netbluemind.folder.api.FolderQuery import __FolderQuerySerDer__
        __data__ = __FolderQuerySerDer__().encode(arg0)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__FolderSerDer__())), response)
    def byPath (self, path ):
        postUri = "/_byPath";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'path': path   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
    def createUserMailFolder (self, imapPath ):
        postUri = "/_createUserMailFolder";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'imapPath': imapPath   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
    def reset (self):
        postUri = "/_reset";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byContentUri (self, uri ):
        postUri = "/by_uri";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'uri': uri   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
    def byId (self, id ):
        postUri = "/by_id";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'id': id   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolderHierarchy_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__FolderSerDer__()), response)
