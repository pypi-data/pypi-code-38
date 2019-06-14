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

class MailFilterRule :
    def __init__( self):
        self.criteria = None
        self.star = None
        self.read = None
        self.delete = None
        self.discard = None
        self.forward = None
        self.deliver = None
        self.active = None
        pass

class __MailFilterRuleSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailFilterRule()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        criteriaValue = value['criteria']
        instance.criteria = serder.STRING.parse(criteriaValue)
        starValue = value['star']
        instance.star = serder.BOOLEAN.parse(starValue)
        readValue = value['read']
        instance.read = serder.BOOLEAN.parse(readValue)
        deleteValue = value['delete']
        instance.delete = serder.BOOLEAN.parse(deleteValue)
        discardValue = value['discard']
        instance.discard = serder.BOOLEAN.parse(discardValue)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        forwardValue = value['forward']
        instance.forward = __MailFilterForwardingSerDer__().parse(forwardValue)
        deliverValue = value['deliver']
        instance.deliver = serder.STRING.parse(deliverValue)
        activeValue = value['active']
        instance.active = serder.BOOLEAN.parse(activeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        criteriaValue = value.criteria
        instance["criteria"] = serder.STRING.encode(criteriaValue)
        starValue = value.star
        instance["star"] = serder.BOOLEAN.encode(starValue)
        readValue = value.read
        instance["read"] = serder.BOOLEAN.encode(readValue)
        deleteValue = value.delete
        instance["delete"] = serder.BOOLEAN.encode(deleteValue)
        discardValue = value.discard
        instance["discard"] = serder.BOOLEAN.encode(discardValue)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        forwardValue = value.forward
        instance["forward"] = __MailFilterForwardingSerDer__().encode(forwardValue)
        deliverValue = value.deliver
        instance["deliver"] = serder.STRING.encode(deliverValue)
        activeValue = value.active
        instance["active"] = serder.BOOLEAN.encode(activeValue)
        return instance

