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

from netbluemind.directory.api.DirBaseValue import DirBaseValue
from netbluemind.directory.api.DirBaseValue import __DirBaseValueSerDer__
class User (DirBaseValue):
    def __init__( self):
        DirBaseValue.__init__(self)
        self.login = None
        self.password = None
        self.contactInfos = None
        self.routing = None
        self.accountType = None
        self.quota = None
        self.properties = None
        pass

class __UserSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = User()
        __DirBaseValueSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        loginValue = value['login']
        instance.login = serder.STRING.parse(loginValue)
        passwordValue = value['password']
        instance.password = serder.STRING.parse(passwordValue)
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        contactInfosValue = value['contactInfos']
        instance.contactInfos = __VCardSerDer__().parse(contactInfosValue)
        from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
        from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
        routingValue = value['routing']
        instance.routing = __MailboxRoutingSerDer__().parse(routingValue)
        from netbluemind.directory.api.BaseDirEntryAccountType import BaseDirEntryAccountType
        from netbluemind.directory.api.BaseDirEntryAccountType import __BaseDirEntryAccountTypeSerDer__
        accountTypeValue = value['accountType']
        instance.accountType = __BaseDirEntryAccountTypeSerDer__().parse(accountTypeValue)
        quotaValue = value['quota']
        instance.quota = serder.INT.parse(quotaValue)
        propertiesValue = value['properties']
        instance.properties = serder.MapSerDer(serder.STRING).parse(propertiesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __DirBaseValueSerDer__().encodeInternal(value,instance)

        loginValue = value.login
        instance["login"] = serder.STRING.encode(loginValue)
        passwordValue = value.password
        instance["password"] = serder.STRING.encode(passwordValue)
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        contactInfosValue = value.contactInfos
        instance["contactInfos"] = __VCardSerDer__().encode(contactInfosValue)
        from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
        from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
        routingValue = value.routing
        instance["routing"] = __MailboxRoutingSerDer__().encode(routingValue)
        from netbluemind.directory.api.BaseDirEntryAccountType import BaseDirEntryAccountType
        from netbluemind.directory.api.BaseDirEntryAccountType import __BaseDirEntryAccountTypeSerDer__
        accountTypeValue = value.accountType
        instance["accountType"] = __BaseDirEntryAccountTypeSerDer__().encode(accountTypeValue)
        quotaValue = value.quota
        instance["quota"] = serder.INT.encode(quotaValue)
        propertiesValue = value.properties
        instance["properties"] = serder.MapSerDer(serder.STRING).encode(propertiesValue)
        return instance

