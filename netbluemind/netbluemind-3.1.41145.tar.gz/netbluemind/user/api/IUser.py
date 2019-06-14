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

IUser_VERSION = "3.1.41145"

class IUser(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/users/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def setPassword (self, uid , password ):
        postUri = "/{uid}/password_";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.user.api.ChangePassword import ChangePassword
        from netbluemind.user.api.ChangePassword import __ChangePasswordSerDer__
        __data__ = __ChangePasswordSerDer__().encode(password)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getPhoto (self, uid ):
        postUri = "/{uid}/photo";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def allUids (self):
        postUri = "/_alluids";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def update (self, uid , user ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        __data__ = __UserSerDer__().encode(user)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getVCard (self, uid ):
        postUri = "/{uid}/vcard";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        return self.handleResult__(__VCardSerDer__(), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def deletePhoto (self, uid ):
        postUri = "/{uid}/photo";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updateAccountType (self, uid , accountType ):
        postUri = "/_updateAccountType/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.directory.api.BaseDirEntryAccountType import BaseDirEntryAccountType
        from netbluemind.directory.api.BaseDirEntryAccountType import __BaseDirEntryAccountTypeSerDer__
        __data__ = __BaseDirEntryAccountTypeSerDer__().encode(accountType)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getResolvedRoles (self, uid ):
        postUri = "/{uid}/roles_resolved";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def byLogin (self, login ):
        postUri = "/byLogin/{login}";
        __data__ = None
        postUri = postUri.replace("{login}",login);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
    def byEmail (self, email ):
        postUri = "/byEmail/{email}";
        __data__ = None
        postUri = postUri.replace("{email}",email);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
    def create (self, uid , user ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        __data__ = __UserSerDer__().encode(user)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def memberOf (self, uid ):
        postUri = "/{uid}/groups";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
    def memberOfGroups (self, uid ):
        postUri = "/{uid}/groupUids";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def setRoles (self, uid , roles ):
        postUri = "/{uid}/roles";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.SetSerDer(serder.STRING).encode(roles)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getRoles (self, uid ):
        postUri = "/{uid}/roles";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def updateVCard (self, uid , userVCard ):
        postUri = "/{uid}/vcard";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        __data__ = __VCardSerDer__().encode(userVCard)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def checkAll (self):
        postUri = "/_check-all";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def byExtId (self, extid ):
        postUri = "/byExtId/{extid}";
        __data__ = None
        postUri = postUri.replace("{extid}",extid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
    def checkAndRepair (self, uid ):
        postUri = "/{uid}/_check-and-repair";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def setExtId (self, uid , arg1 ):
        postUri = "/{uid}/_extId";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.STRING.encode(arg1)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def check (self, uid ):
        postUri = "/{uid}/_check";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getIcon (self, uid ):
        postUri = "/{uid}/icon";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ByteArraySerDer, response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
    def setPhoto (self, uid , arg1 ):
        postUri = "/{uid}/photo";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.ByteArraySerDer.encode(arg1)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getUsersWithRoles (self, roles ):
        postUri = "/_roleusers";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(roles)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.SetSerDer(serder.STRING), response)
    def createWithExtId (self, uid , extid , user ):
        postUri = "/{uid}/{extid}/createwithextid";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{extid}",extid);
        from netbluemind.user.api.User import User
        from netbluemind.user.api.User import __UserSerDer__
        __data__ = __UserSerDer__().encode(user)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def checkAndRepairAll (self):
        postUri = "/_check-and-repair-all";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IUser_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
