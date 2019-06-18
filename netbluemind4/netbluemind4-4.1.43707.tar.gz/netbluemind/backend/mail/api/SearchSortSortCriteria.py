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

class SearchSortSortCriteria :
    def __init__( self):
        self.field = None
        self.order = None
        pass

class __SearchSortSortCriteriaSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SearchSortSortCriteria()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        fieldValue = value['field']
        instance.field = serder.STRING.parse(fieldValue)
        from netbluemind.backend.mail.api.SearchSortOrder import SearchSortOrder
        from netbluemind.backend.mail.api.SearchSortOrder import __SearchSortOrderSerDer__
        orderValue = value['order']
        instance.order = __SearchSortOrderSerDer__().parse(orderValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        fieldValue = value.field
        instance["field"] = serder.STRING.encode(fieldValue)
        from netbluemind.backend.mail.api.SearchSortOrder import SearchSortOrder
        from netbluemind.backend.mail.api.SearchSortOrder import __SearchSortOrderSerDer__
        orderValue = value.order
        instance["order"] = __SearchSortOrderSerDer__().encode(orderValue)
        return instance

