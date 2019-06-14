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

IMailboxes_VERSION = "3.1.41145"

class IMailboxes(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mailboxes/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def getMailboxConfig (self, uid ):
        postUri = "/{uid}/_config";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.MailboxConfig import MailboxConfig
        from netbluemind.mailbox.api.MailboxConfig import __MailboxConfigSerDer__
        return self.handleResult__(__MailboxConfigSerDer__(), response)
    def update (self, uid , mailbox ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        __data__ = __MailboxSerDer__().encode(mailbox)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byName (self, name ):
        postUri = "/_byname";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'name': name   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def setMailboxFilter (self, mailboxUid , filter ):
        postUri = "/{mailboxUid}/_filter";
        __data__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        __data__ = __MailFilterSerDer__().encode(filter)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getUnreadMessagesCount (self):
        postUri = "/_unread";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(serder.INT, response)
    def setMailboxAccessControlList (self, mailboxUid , accessControlEntries ):
        postUri = "/{mailboxUid}/_acls";
        __data__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        __data__ = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(accessControlEntries)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byEmail (self, email ):
        postUri = "/_byemail";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'email': email   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
    def create (self, uid , mailbox ):
        postUri = "/{uid}";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        __data__ = __MailboxSerDer__().encode(mailbox)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def byRouting (self, email ):
        postUri = "/_byRouting";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'email': email   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def checkAll (self):
        postUri = "/_check-all";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def multipleGet (self, uids ):
        postUri = "/_mget";
        __data__ = None
        __data__ = serder.ListSerDer(serder.STRING).encode(uids)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)
    def checkAndRepair (self, uid ):
        postUri = "/{uid}/_check-and-repair";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def getMailboxFilter (self, mailboxUid ):
        postUri = "/{mailboxUid}/_filter";
        __data__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        return self.handleResult__(__MailFilterSerDer__(), response)
    def getMailboxAccessControlList (self, mailboxUid ):
        postUri = "/{mailboxUid}/_acls";
        __data__ = None
        postUri = postUri.replace("{mailboxUid}",mailboxUid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
        from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
        return self.handleResult__(serder.ListSerDer(__AccessControlEntrySerDer__()), response)
    def check (self, uid ):
        postUri = "/{uid}/_check";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def list (self):
        postUri = "/_list";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)
    def setDomainFilter (self, filter ):
        postUri = "/_filter";
        __data__ = None
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        __data__ = __MailFilterSerDer__().encode(filter)

        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getMailboxQuota (self, uid ):
        postUri = "/{uid}/_quota";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.MailboxQuota import MailboxQuota
        from netbluemind.mailbox.api.MailboxQuota import __MailboxQuotaSerDer__
        return self.handleResult__(__MailboxQuotaSerDer__(), response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        postUri = postUri.replace("{uid}",uid);
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.Mailbox import Mailbox
        from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
    def getDomainFilter (self):
        postUri = "/_filter";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.mailbox.api.MailFilter import MailFilter
        from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
        return self.handleResult__(__MailFilterSerDer__(), response)
    def byType (self, email ):
        postUri = "/_byType";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  'email': email   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def checkAndRepairAll (self):
        postUri = "/_check-and-repair-all";
        __data__ = None
        __encoded__ = None
        __encoded__ = json.dumps(__data__)
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxes_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
