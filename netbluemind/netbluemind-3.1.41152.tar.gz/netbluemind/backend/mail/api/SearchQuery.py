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

class SearchQuery :
    def __init__( self):
        self.searchSessionId = None
        self.query = None
        self.maxResults = None
        self.offset = None
        self.scope = None
        pass

class __SearchQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SearchQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        searchSessionIdValue = value['searchSessionId']
        instance.searchSessionId = serder.STRING.parse(searchSessionIdValue)
        queryValue = value['query']
        instance.query = serder.STRING.parse(queryValue)
        maxResultsValue = value['maxResults']
        instance.maxResults = serder.LONG.parse(maxResultsValue)
        offsetValue = value['offset']
        instance.offset = serder.LONG.parse(offsetValue)
        from netbluemind.backend.mail.api.SearchQuerySearchScope import SearchQuerySearchScope
        from netbluemind.backend.mail.api.SearchQuerySearchScope import __SearchQuerySearchScopeSerDer__
        scopeValue = value['scope']
        instance.scope = __SearchQuerySearchScopeSerDer__().parse(scopeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        searchSessionIdValue = value.searchSessionId
        instance["searchSessionId"] = serder.STRING.encode(searchSessionIdValue)
        queryValue = value.query
        instance["query"] = serder.STRING.encode(queryValue)
        maxResultsValue = value.maxResults
        instance["maxResults"] = serder.LONG.encode(maxResultsValue)
        offsetValue = value.offset
        instance["offset"] = serder.LONG.encode(offsetValue)
        from netbluemind.backend.mail.api.SearchQuerySearchScope import SearchQuerySearchScope
        from netbluemind.backend.mail.api.SearchQuerySearchScope import __SearchQuerySearchScopeSerDer__
        scopeValue = value.scope
        instance["scope"] = __SearchQuerySearchScopeSerDer__().encode(scopeValue)
        return instance

