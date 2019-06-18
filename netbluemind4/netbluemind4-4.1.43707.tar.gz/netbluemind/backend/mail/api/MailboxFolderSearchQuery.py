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

class MailboxFolderSearchQuery :
    def __init__( self):
        self.query = None
        self.sort = None
        pass

class __MailboxFolderSearchQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailboxFolderSearchQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.backend.mail.api.SearchQuery import SearchQuery
        from netbluemind.backend.mail.api.SearchQuery import __SearchQuerySerDer__
        queryValue = value['query']
        instance.query = __SearchQuerySerDer__().parse(queryValue)
        from netbluemind.backend.mail.api.SearchSort import SearchSort
        from netbluemind.backend.mail.api.SearchSort import __SearchSortSerDer__
        sortValue = value['sort']
        instance.sort = __SearchSortSerDer__().parse(sortValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.backend.mail.api.SearchQuery import SearchQuery
        from netbluemind.backend.mail.api.SearchQuery import __SearchQuerySerDer__
        queryValue = value.query
        instance["query"] = __SearchQuerySerDer__().encode(queryValue)
        from netbluemind.backend.mail.api.SearchSort import SearchSort
        from netbluemind.backend.mail.api.SearchSort import __SearchSortSerDer__
        sortValue = value.sort
        instance["sort"] = __SearchSortSerDer__().encode(sortValue)
        return instance

