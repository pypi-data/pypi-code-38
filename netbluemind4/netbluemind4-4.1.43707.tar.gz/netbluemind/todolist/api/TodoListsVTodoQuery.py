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
from netbluemind.python import serder

class TodoListsVTodoQuery :
    def __init__( self):
        self.owner = None
        self.containers = None
        self.vtodoQuery = None
        pass

class __TodoListsVTodoQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = TodoListsVTodoQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        ownerValue = value['owner']
        instance.owner = serder.STRING.parse(ownerValue)
        containersValue = value['containers']
        instance.containers = serder.ListSerDer(serder.STRING).parse(containersValue)
        from netbluemind.todolist.api.VTodoQuery import VTodoQuery
        from netbluemind.todolist.api.VTodoQuery import __VTodoQuerySerDer__
        vtodoQueryValue = value['vtodoQuery']
        instance.vtodoQuery = __VTodoQuerySerDer__().parse(vtodoQueryValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        ownerValue = value.owner
        instance["owner"] = serder.STRING.encode(ownerValue)
        containersValue = value.containers
        instance["containers"] = serder.ListSerDer(serder.STRING).encode(containersValue)
        from netbluemind.todolist.api.VTodoQuery import VTodoQuery
        from netbluemind.todolist.api.VTodoQuery import __VTodoQuerySerDer__
        vtodoQueryValue = value.vtodoQuery
        instance["vtodoQuery"] = __VTodoQuerySerDer__().encode(vtodoQueryValue)
        return instance

