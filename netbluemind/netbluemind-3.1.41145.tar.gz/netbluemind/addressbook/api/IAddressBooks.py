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

IAddressBooks_VERSION = "3.1.41145"

class IAddressBooks(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/addressbooks'

    def search (self, query ):
        postUri = "/_search";
        __data__ = None
        from netbluemind.addressbook.api.VCardQuery import VCardQuery
        from netbluemind.addressbook.api.VCardQuery import __VCardQuerySerDer__
        __data__ = __VCardQuerySerDer__().encode(query)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAddressBooks_VERSION}, data = __encoded__);
        from netbluemind.addressbook.api.VCardInfo import VCardInfo
        from netbluemind.addressbook.api.VCardInfo import __VCardInfoSerDer__
        from netbluemind.core.container.model.ItemContainerValue import ItemContainerValue
        from netbluemind.core.container.model.ItemContainerValue import __ItemContainerValueSerDer__
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(__ItemContainerValueSerDer__(__VCardInfoSerDer__())), response)
