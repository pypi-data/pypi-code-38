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

ITodoLists_VERSION = "3.1.41145"

class ITodoLists(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/todolists'

    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.todolist.api.TodoListsVTodoQuery import TodoListsVTodoQuery
        from netbluemind.todolist.api.TodoListsVTodoQuery import __TodoListsVTodoQuerySerDer__
        __data__ = __TodoListsVTodoQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoLists_VERSION}, data = __encoded__);
        from netbluemind.todolist.api.VTodo import VTodo
        from netbluemind.todolist.api.VTodo import __VTodoSerDer__
        from netbluemind.core.container.model.ItemContainerValue import ItemContainerValue
        from netbluemind.core.container.model.ItemContainerValue import __ItemContainerValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemContainerValueSerDer__(__VTodoSerDer__())), response)
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

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoLists_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ITodoLists_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
