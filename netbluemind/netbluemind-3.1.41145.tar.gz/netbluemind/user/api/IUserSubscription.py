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

IUserSubscription_VERSION = "3.1.41145"

class IUserSubscription(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/users/{domainUid}/subscriptions'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def subscribe (self, subject , subscriptions ):
        postUri = "/{subject}/_subscribe";
        __data__ = None
        postUri = postUri.replace("{subject}",subject);
        from netbluemind.core.container.api.ContainerSubscription import ContainerSubscription
        from netbluemind.core.container.api.ContainerSubscription import __ContainerSubscriptionSerDer__
        __data__ = serder.ListSerDer(__ContainerSubscriptionSerDer__()).encode(subscriptions)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserSubscription_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def unsubscribe (self, subject , containers ):
        postUri = "/{subject}/_unsubscribe";
        __data__ = None
        postUri = postUri.replace("{subject}",subject);
        __data__ = serder.ListSerDer(serder.STRING).encode(containers)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserSubscription_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def listSubscriptions (self, subject , type ):
        postUri = "/{subject}";
        __data__ = None
        postUri = postUri.replace("{subject}",subject);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   'type': type   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUserSubscription_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
        from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
        return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
