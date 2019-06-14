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

IInstallation_VERSION = "3.1.41145"

class IInstallation(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/system/installation'

    def getSystemState (self):
        postUri = "/state";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.SystemState import SystemState
        from netbluemind.system.api.SystemState import __SystemStateSerDer__
        return self.handleResult__(__SystemStateSerDer__(), response)
    def removeSubscription (self):
        postUri = "/subscription";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def runningMode (self):
        postUri = "/state/_maintenance";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def setSubscriptionContacts (self, emails ):
        postUri = "/_subscriptionContacts";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(emails)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getSubscriptionContacts (self):
        postUri = "/_subscriptionContacts";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def markSchemaAsUpgraded (self):
        postUri = "/version";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def upgradeStatus (self):
        postUri = "/_upgrade";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.UpgradeStatus import UpgradeStatus
        from netbluemind.system.api.UpgradeStatus import __UpgradeStatusSerDer__
        return self.handleResult__(__UpgradeStatusSerDer__(), response)
    def getInfos (self):
        postUri = "/_infos";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.PublicInfos import PublicInfos
        from netbluemind.system.api.PublicInfos import __PublicInfosSerDer__
        return self.handleResult__(__PublicInfosSerDer__(), response)
    def resetIndexes (self):
        postUri = "/_resetIndexes";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def deleteLogo (self):
        postUri = "/logo";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getVersion (self):
        postUri = "/version";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.InstallationVersion import InstallationVersion
        from netbluemind.system.api.InstallationVersion import __InstallationVersionSerDer__
        return self.handleResult__(__InstallationVersionSerDer__(), response)
    def setLogo (self, logo ):
        postUri = "/logo";
        __data__ = None
        __data__ = serder.ByteArraySerDer.encode(logo)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getLogo (self):
        postUri = "/logo";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.CustomLogo import CustomLogo
        from netbluemind.system.api.CustomLogo import __CustomLogoSerDer__
        return self.handleResult__(__CustomLogoSerDer__(), response)
    def upgrade (self):
        postUri = "/_upgrade";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def updateSubscription (self, licence ):
        postUri = "/subscription";
        __data__ = None
        __data__ = serder.STRING.encode(licence)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updateSubscriptionWithArchive (self, archive ):
        postUri = "/subscription/_archive";
        __data__ = None
        __data__ = serder.STREAM.encode(archive)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getSubscriptionInformations (self):
        postUri = "/subscription";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.system.api.SubscriptionInformations import SubscriptionInformations
        from netbluemind.system.api.SubscriptionInformations import __SubscriptionInformationsSerDer__
        return self.handleResult__(__SubscriptionInformationsSerDer__(), response)
    def initialize (self):
        postUri = "/_initialize";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def maintenanceMode (self):
        postUri = "/state/_maintenance";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def partialUpgrade (self, from_ , to ):
        postUri = "/_partialUpgrade";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'from': from_  , 'to': to   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInstallation_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
