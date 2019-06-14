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

IMailboxFolders_VERSION = "4.1.42538"

class IMailboxFolders(BaseEndpoint):
    def __init__(self, apiKey, url ,partition ,mailboxRoot ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mail_folders/{partition}/{mailboxRoot}'
        self.partition_ = partition
        self.base = self.base.replace('{partition}',partition)
        self.mailboxRoot_ = mailboxRoot
        self.base = self.base.replace('{mailboxRoot}',mailboxRoot)

    def importItems (self, folderDestinationId , mailboxItems ):
        postUri = "/importItems/{folderDestinationId}";
        __data__ = None
        postUri = postUri.replace("{folderDestinationId}",folderDestinationId);
        from netbluemind.backend.mail.api.ImportMailboxItemSet import ImportMailboxItemSet
        from netbluemind.backend.mail.api.ImportMailboxItemSet import __ImportMailboxItemSetSerDer__
        __data__ = __ImportMailboxItemSetSerDer__().encode(mailboxItems)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.ImportMailboxItemsStatus import ImportMailboxItemsStatus
        from netbluemind.backend.mail.api.ImportMailboxItemsStatus import __ImportMailboxItemsStatusSerDer__
        return self.handleResult__(__ImportMailboxItemsStatusSerDer__(), response)
    def filteredChangesetById (self, since , arg1 ):
        postUri = "/_filteredChangesetById";
        __data__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg1)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)
    def byName (self, name ):
        postUri = "/byName/{name}";
        __data__ = None
        postUri = postUri.replace("{name}",name);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxFolderSerDer__()), response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def changesetById (self, since ):
        postUri = "/_changesetById";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
    def emptyFolder (self, id ):
        postUri = "/empty/{id}";
        __data__ = None
        postUri = postUri.replace("{id}",id);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getCompleteById (self, id ):
        postUri = "/{id}/completeById";
        __data__ = None
        postUri = postUri.replace("{id}",id);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxFolderSerDer__()), response)
    def searchItems (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.backend.mail.api.MailboxFolderSearchQuery import MailboxFolderSearchQuery
        from netbluemind.backend.mail.api.MailboxFolderSearchQuery import __MailboxFolderSearchQuerySerDer__
        __data__ = __MailboxFolderSearchQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.SearchResult import SearchResult
        from netbluemind.backend.mail.api.SearchResult import __SearchResultSerDer__
        return self.handleResult__(__SearchResultSerDer__(), response)
    def all (self):
        postUri = "/_all";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxFolderSerDer__())), response)
    def getVersion (self):
        postUri = "/_version";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        return self.handleResult__(serder.LONG, response)
    def createBasic (self, value ):
        postUri = "";
        __data__ = None
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        __data__ = __MailboxFolderSerDer__().encode(value)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(__ItemIdentifierSerDer__(), response)
    def createForHierarchy (self, hierarchyId , value ):
        postUri = "/id/{hierarchyId}";
        __data__ = None
        postUri = postUri.replace("{hierarchyId}",hierarchyId);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        __data__ = __MailboxFolderSerDer__().encode(value)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(__ItemIdentifierSerDer__(), response)
    def itemChangelog (self, uid , arg1 ):
        postUri = "/{uid}/_itemchangelog";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.LONG.encode(arg1)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)
    def updateById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        __data__ = __MailboxFolderSerDer__().encode(value)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxFolder import MailboxFolder
        from netbluemind.backend.mail.api.MailboxFolder import __MailboxFolderSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxFolderSerDer__()), response)
    def containerChangelog (self, arg0 ):
        postUri = "/_changelog";
        __data__ = None
        __data__ = serder.LONG.encode(arg0)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def deleteById (self, id ):
        postUri = "/id/{id}";
        __data__ = None
        postUri = postUri.replace("{id}",id);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def deepDelete (self, id ):
        postUri = "/deep/{id}";
        __data__ = None
        postUri = postUri.replace("{id}",id);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxFolders_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
