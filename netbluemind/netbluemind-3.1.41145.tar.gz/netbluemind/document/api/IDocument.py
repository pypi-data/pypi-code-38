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

IDocument_VERSION = "3.1.41145"

class IDocument(BaseEndpoint):
    def __init__(self, apiKey, url ,containerUid ,itemUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/document/{containerUid}/{itemUid}'
        self.containerUid_ = containerUid
        self.base = self.base.replace('{containerUid}',containerUid)
        self.itemUid_ = itemUid
        self.base = self.base.replace('{itemUid}',itemUid)

    def update (self, uid , doc ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.document.api.Document import Document
        from netbluemind.document.api.Document import __DocumentSerDer__
        __data__ = __DocumentSerDer__().encode(doc)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def list (self):
        postUri = "/_list";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        from netbluemind.document.api.DocumentMetadata import DocumentMetadata
        from netbluemind.document.api.DocumentMetadata import __DocumentMetadataSerDer__
        return self.handleResult__(serder.ListSerDer(__DocumentMetadataSerDer__()), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def fetchMetadata (self, uid ):
        postUri = "/{uid}/metadata";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        from netbluemind.document.api.DocumentMetadata import DocumentMetadata
        from netbluemind.document.api.DocumentMetadata import __DocumentMetadataSerDer__
        return self.handleResult__(__DocumentMetadataSerDer__(), response)
    def fetch (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        from netbluemind.document.api.Document import Document
        from netbluemind.document.api.Document import __DocumentSerDer__
        return self.handleResult__(__DocumentSerDer__(), response)
    def create (self, uid , doc ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.document.api.Document import Document
        from netbluemind.document.api.Document import __DocumentSerDer__
        __data__ = __DocumentSerDer__().encode(doc)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IDocument_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
