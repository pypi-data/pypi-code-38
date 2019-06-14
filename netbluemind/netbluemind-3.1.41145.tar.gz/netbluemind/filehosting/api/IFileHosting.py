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

IFileHosting_VERSION = "3.1.41145"

class IFileHosting(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/filehosting/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def store (self, path , document ):
        postUri = "/{path}";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __data__ = serder.STREAM.encode(document)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def list (self, path ):
        postUri = "/_list";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'path': path   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.FileHostingItem import FileHostingItem
        from netbluemind.filehosting.api.FileHostingItem import __FileHostingItemSerDer__
        return self.handleResult__(serder.ListSerDer(__FileHostingItemSerDer__()), response)
    def delete (self, path ):
        postUri = "/{path}";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getComplete (self, uid ):
        postUri = "/{uid}/_complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.FileHostingItem import FileHostingItem
        from netbluemind.filehosting.api.FileHostingItem import __FileHostingItemSerDer__
        return self.handleResult__(__FileHostingItemSerDer__(), response)
    def getConfiguration (self):
        postUri = "/_config";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.Configuration import Configuration
        from netbluemind.filehosting.api.Configuration import __ConfigurationSerDer__
        return self.handleResult__(__ConfigurationSerDer__(), response)
    def find (self, query ):
        postUri = "/_find";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'query': query   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.FileHostingItem import FileHostingItem
        from netbluemind.filehosting.api.FileHostingItem import __FileHostingItemSerDer__
        return self.handleResult__(serder.ListSerDer(__FileHostingItemSerDer__()), response)
    def unShare (self, url ):
        postUri = "/{url}/unshare";
        __data__ = None
        postUri = postUri.replace("{url}",url);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def get (self, path ):
        postUri = "/{path}/_content";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        return response.content
    def getSharedFile (self, uid ):
        postUri = "/{uid}/_public";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        return response.content
    def share (self, path , downloadLimit , expirationDate ):
        postUri = "/{path}/share";
        __data__ = None
        postUri = postUri.replace("{path}",path);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'downloadLimit': downloadLimit  , 'expirationDate': expirationDate   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.FileHostingPublicLink import FileHostingPublicLink
        from netbluemind.filehosting.api.FileHostingPublicLink import __FileHostingPublicLinkSerDer__
        return self.handleResult__(__FileHostingPublicLinkSerDer__(), response)
    def info (self):
        postUri = "/_info";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IFileHosting_VERSION}, data = __encoded__);
        from netbluemind.filehosting.api.FileHostingInfo import FileHostingInfo
        from netbluemind.filehosting.api.FileHostingInfo import __FileHostingInfoSerDer__
        return self.handleResult__(__FileHostingInfoSerDer__(), response)
