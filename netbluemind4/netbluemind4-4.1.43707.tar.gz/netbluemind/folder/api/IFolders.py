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

IFolders_VERSION = "3.1.41145"

class IFolders(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/ifolders'

    def byUid (self, uid ):
        postUri = "/by_uid";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'uid': uid   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFolders_VERSION}, data = __encoded__);
        from netbluemind.folder.api.Folder import Folder
        from netbluemind.folder.api.Folder import __FolderSerDer__
        return self.handleResult__(__FolderSerDer__(), response)
    def byContentUri (self, uri ):
        postUri = "/by_uri";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'uri': uri   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFolders_VERSION}, data = __encoded__);
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(serder.INT), response)
