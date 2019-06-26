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
class Mailshare (DirBaseValue):
    def __init__( self):
        DirBaseValue.__init__(self)
        self.name = None
        self.quota = None
        self.routing = None
        self.card = None
        pass

class __MailshareSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Mailshare()
        __DirBaseValueSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        quotaValue = value['quota']
        instance.quota = serder.INT.parse(quotaValue)
        from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
        from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
        routingValue = value['routing']
        instance.routing = __MailboxRoutingSerDer__().parse(routingValue)
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        cardValue = value['card']
        instance.card = __VCardSerDer__().parse(cardValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __DirBaseValueSerDer__().encodeInternal(value,instance)

        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        quotaValue = value.quota
        instance["quota"] = serder.INT.encode(quotaValue)
        from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
        from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
        routingValue = value.routing
        instance["routing"] = __MailboxRoutingSerDer__().encode(routingValue)
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        cardValue = value.card
        instance["card"] = __VCardSerDer__().encode(cardValue)
        return instance

