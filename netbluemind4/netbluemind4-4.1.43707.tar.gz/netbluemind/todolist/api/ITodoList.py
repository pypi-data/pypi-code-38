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

ITodoList_VERSION = "4.1.43707"

class ITodoList(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/todolist/{containerUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)

    def filteredChangesetById (self, since , arg1 ):
        postUri = "/_filteredChangesetById";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)
    def allUids (self):
        postUri = "/_all";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def update (self, uid , todo ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        __data__ = __VTodoSerDer__().encode(todo)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updates (self, changes ):
        postUri = "/_mupdates";
        __data__ = None
        __encoded__ = None
        from netbluemind.todolist.api.VTodoChanges import VTodoChanges
        from netbluemind.todolist.api.VTodoChanges import __VTodoChangesSerDer__
        __data__ = __VTodoChangesSerDer__().encode(changes)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerUpdatesResult import ContainerUpdatesResult
        from netbluemind.core.container.model.ContainerUpdatesResult import __ContainerUpdatesResultSerDer__
        return self.handleResult__(__ContainerUpdatesResultSerDer__(), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def changesetById (self, since ):
        postUri = "/_changesetById";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        __encoded__ = None
        from netbluemind.todolist.api.VTodoQuery import VTodoQuery
        from netbluemind.todolist.api.VTodoQuery import __VTodoQuerySerDer__
        __data__ = __VTodoQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VTodoSerDer__())), response)
    def getReminder (self, dtalarm ):
        postUri = "/_remimder";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        __data__ = __BmDateTimeSerDer__().encode(dtalarm)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.Reminder import Reminder
        from netbluemind.todolist.api.Reminder import __ReminderSerDer__
        return self.handleResult__(serder.ListSerDer(__ReminderSerDer__()), response)
    def create (self, uid , todo ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        __data__ = __VTodoSerDer__().encode(todo)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def copy (self, uids , destContainerUid ):
        postUri = "/_copy/{destContainerUid}";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        postUri = postUri.replace("{destContainerUid}",destContainerUid);
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getCompleteById (self, id ):
        postUri = "/{id}/completeById";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__VTodoSerDer__()), response)
    def all (self):
        postUri = "";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VTodoSerDer__())), response)
    def getVersion (self):
        postUri = "/_version";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(serder.LONG, response)
    def move (self, uids , destContainerUid ):
        postUri = "/_move/{destContainerUid}";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        postUri = postUri.replace("{destContainerUid}",destContainerUid);
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def multipleGet (self, uids ):
        postUri = "/_mget";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VTodoSerDer__())), response)
    def count (self, arg0 ):
        postUri = "/_count";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Count import Count
        from netbluemind.core.container.api.Count import __CountSerDer__
        return self.handleResult__(__CountSerDer__(), response)
    def sortedIds (self, sorted ):
        postUri = "/_sorted";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.SortDescriptor import SortDescriptor
        from netbluemind.core.container.model.SortDescriptor import __SortDescriptorSerDer__
        __data__ = __SortDescriptorSerDer__().encode(sorted)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.LONG), response)
    def sync (self, since , changes ):
        postUri = "/_sync";
        __data__ = None
        __encoded__ = None
        from netbluemind.todolist.api.VTodoChanges import VTodoChanges
        from netbluemind.todolist.api.VTodoChanges import __VTodoChangesSerDer__
        __data__ = __VTodoChangesSerDer__().encode(changes)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def itemChangelog (self, uid , arg1 ):
        postUri = "/{uid}/_itemchangelog";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.LONG.encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)
    def multipleDeleteById (self, arg0 ):
        postUri = "/_multipleDelete";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updateById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        __data__ = __VTodoSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__VTodoSerDer__()), response)
    def containerChangelog (self, arg0 ):
        postUri = "/_changelog";
        __data__ = None
        __encoded__ = None
        __data__ = serder.LONG.encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def deleteById (self, id ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def reset (self):
        postUri = "/_reset";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def createById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        __data__ = __VTodoSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoList_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
