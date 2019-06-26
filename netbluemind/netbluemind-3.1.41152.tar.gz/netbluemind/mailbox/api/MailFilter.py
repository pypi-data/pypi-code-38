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

class MailFilter :
    def __init__( self):
        self.rules = None
        self.forwarding = None
        self.vacation = None
        pass

class __MailFilterSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailFilter()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.mailbox.api.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.MailFilterRule import __MailFilterRuleSerDer__
        rulesValue = value['rules']
        instance.rules = serder.ListSerDer(__MailFilterRuleSerDer__()).parse(rulesValue)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        forwardingValue = value['forwarding']
        instance.forwarding = __MailFilterForwardingSerDer__().parse(forwardingValue)
        from netbluemind.mailbox.api.MailFilterVacation import MailFilterVacation
        from netbluemind.mailbox.api.MailFilterVacation import __MailFilterVacationSerDer__
        vacationValue = value['vacation']
        instance.vacation = __MailFilterVacationSerDer__().parse(vacationValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.mailbox.api.MailFilterRule import MailFilterRule
        from netbluemind.mailbox.api.MailFilterRule import __MailFilterRuleSerDer__
        rulesValue = value.rules
        instance["rules"] = serder.ListSerDer(__MailFilterRuleSerDer__()).encode(rulesValue)
        from netbluemind.mailbox.api.MailFilterForwarding import MailFilterForwarding
        from netbluemind.mailbox.api.MailFilterForwarding import __MailFilterForwardingSerDer__
        forwardingValue = value.forwarding
        instance["forwarding"] = __MailFilterForwardingSerDer__().encode(forwardingValue)
        from netbluemind.mailbox.api.MailFilterVacation import MailFilterVacation
        from netbluemind.mailbox.api.MailFilterVacation import __MailFilterVacationSerDer__
        vacationValue = value.vacation
        instance["vacation"] = __MailFilterVacationSerDer__().encode(vacationValue)
        return instance

