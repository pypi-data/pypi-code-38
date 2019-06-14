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

IDirectory_VERSION = "3.1.41145"

class IDirectory(BaseEndpoint):
    def __init__(self, apiKey, url ,domain ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/directory/{domain}'
        self.domain_ = domain
        self.base = self.base.replace('{domain}',domain)

    def getEntryIcon (self, entryUid ):
        postUri = "/entry-uid/{entryUid}/icon";
        __data__ = None
        postUri = postUri.replace("{entryUid}",entryUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def getVCard (self, uid ):
        postUri = "/{uid}/_vcard";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__VCardSerDer__()), response)
    def delete (self, path ):
        postUri = "/{path}";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.directory.api.DirEntryQuery import DirEntryQuery
        from netbluemind.directory.api.DirEntryQuery import __DirEntryQuerySerDer__
        __data__ = __DirEntryQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__DirEntrySerDer__())), response)
    def findByEntryUid (self, entryUid ):
        postUri = "/entry-uid/{entryUid}";
        __data__ = None
        postUri = postUri.replace("{entryUid}",entryUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        return self.handleResult__(__DirEntrySerDer__(), response)
    def getEntryPhoto (self, entryUid ):
        postUri = "/entry-uid/{entryUid}/photo";
        __data__ = None
        postUri = postUri.replace("{entryUid}",entryUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def getEntry (self, path ):
        postUri = "/_entry";
        __data__ = None
        __data__ = serder.STRING.encode(path)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        return self.handleResult__(__DirEntrySerDer__(), response)
    def getRoot (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        return self.handleResult__(__DirEntrySerDer__(), response)
    def deleteByEntryUid (self, entryUid ):
        postUri = "/_byentryuid/{entryUid}";
        __data__ = None
        postUri = postUri.replace("{entryUid}",entryUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getByEmail (self, email ):
        postUri = "/_byEmail/{email}";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        return self.handleResult__(__DirEntrySerDer__(), response)
    def getRolesForDirEntry (self, entryUid ):
        postUri = "/entry-uid/{entryUid}/rolesfor_";
        __data__ = None
        postUri = postUri.replace("{entryUid}",entryUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def changelog (self, since ):
        postUri = "/_changelog";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def getRolesForOrgUnit (self, ouUid ):
        postUri = "/ou-uid/{ouUid}/rolesfor_";
        __data__ = None
        postUri = postUri.replace("{ouUid}",ouUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def getIcon (self, path ):
        postUri = "/_icon/{path}";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def getEntries (self, path ):
        postUri = "/_childs";
        __data__ = None
        __data__ = serder.STRING.encode(path)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDirectory_VERSION}, data = __encoded__);
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        return self.handleResult__(serder.ListSerDer(__DirEntrySerDer__()), response)
