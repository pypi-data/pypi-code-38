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

class SubscriptionInformations :
    def __init__( self):
        self.version = None
        self.installationVersion = None
        self.customer = None
        self.customerCode = None
        self.dealer = None
        self.distributor = None
        self.kind = None
        self.starts = None
        self.ends = None
        self.valid = None
        self.pubKeyFingerprint = None
        self.validProvider = None
        self.fromTechVersion = None
        self.indicator = None
        self.contacts = None
        self.messages = None
        pass

class __SubscriptionInformationsSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = SubscriptionInformations()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        versionValue = value['version']
        instance.version = serder.STRING.parse(versionValue)
        installationVersionValue = value['installationVersion']
        instance.installationVersion = serder.STRING.parse(installationVersionValue)
        customerValue = value['customer']
        instance.customer = serder.STRING.parse(customerValue)
        customerCodeValue = value['customerCode']
        instance.customerCode = serder.STRING.parse(customerCodeValue)
        dealerValue = value['dealer']
        instance.dealer = serder.STRING.parse(dealerValue)
        distributorValue = value['distributor']
        instance.distributor = serder.STRING.parse(distributorValue)
        from netbluemind.system.api.SubscriptionInformationsKind import SubscriptionInformationsKind
        from netbluemind.system.api.SubscriptionInformationsKind import __SubscriptionInformationsKindSerDer__
        kindValue = value['kind']
        instance.kind = __SubscriptionInformationsKindSerDer__().parse(kindValue)
        startsValue = value['starts']
        instance.starts = serder.DATE.parse(startsValue)
        endsValue = value['ends']
        instance.ends = serder.DATE.parse(endsValue)
        validValue = value['valid']
        instance.valid = serder.BOOLEAN.parse(validValue)
        pubKeyFingerprintValue = value['pubKeyFingerprint']
        instance.pubKeyFingerprint = serder.STRING.parse(pubKeyFingerprintValue)
        validProviderValue = value['validProvider']
        instance.validProvider = serder.BOOLEAN.parse(validProviderValue)
        fromTechVersionValue = value['fromTechVersion']
        instance.fromTechVersion = serder.STRING.parse(fromTechVersionValue)
        from netbluemind.system.api.SubscriptionInformationsInstallationIndicator import SubscriptionInformationsInstallationIndicator
        from netbluemind.system.api.SubscriptionInformationsInstallationIndicator import __SubscriptionInformationsInstallationIndicatorSerDer__
        indicatorValue = value['indicator']
        instance.indicator = serder.ListSerDer(__SubscriptionInformationsInstallationIndicatorSerDer__()).parse(indicatorValue)
        contactsValue = value['contacts']
        instance.contacts = serder.ListSerDer(serder.STRING).parse(contactsValue)
        from netbluemind.system.api.SubscriptionInformationsMessage import SubscriptionInformationsMessage
        from netbluemind.system.api.SubscriptionInformationsMessage import __SubscriptionInformationsMessageSerDer__
        messagesValue = value['messages']
        instance.messages = serder.ListSerDer(__SubscriptionInformationsMessageSerDer__()).parse(messagesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        versionValue = value.version
        instance["version"] = serder.STRING.encode(versionValue)
        installationVersionValue = value.installationVersion
        instance["installationVersion"] = serder.STRING.encode(installationVersionValue)
        customerValue = value.customer
        instance["customer"] = serder.STRING.encode(customerValue)
        customerCodeValue = value.customerCode
        instance["customerCode"] = serder.STRING.encode(customerCodeValue)
        dealerValue = value.dealer
        instance["dealer"] = serder.STRING.encode(dealerValue)
        distributorValue = value.distributor
        instance["distributor"] = serder.STRING.encode(distributorValue)
        from netbluemind.system.api.SubscriptionInformationsKind import SubscriptionInformationsKind
        from netbluemind.system.api.SubscriptionInformationsKind import __SubscriptionInformationsKindSerDer__
        kindValue = value.kind
        instance["kind"] = __SubscriptionInformationsKindSerDer__().encode(kindValue)
        startsValue = value.starts
        instance["starts"] = serder.DATE.encode(startsValue)
        endsValue = value.ends
        instance["ends"] = serder.DATE.encode(endsValue)
        validValue = value.valid
        instance["valid"] = serder.BOOLEAN.encode(validValue)
        pubKeyFingerprintValue = value.pubKeyFingerprint
        instance["pubKeyFingerprint"] = serder.STRING.encode(pubKeyFingerprintValue)
        validProviderValue = value.validProvider
        instance["validProvider"] = serder.BOOLEAN.encode(validProviderValue)
        fromTechVersionValue = value.fromTechVersion
        instance["fromTechVersion"] = serder.STRING.encode(fromTechVersionValue)
        from netbluemind.system.api.SubscriptionInformationsInstallationIndicator import SubscriptionInformationsInstallationIndicator
        from netbluemind.system.api.SubscriptionInformationsInstallationIndicator import __SubscriptionInformationsInstallationIndicatorSerDer__
        indicatorValue = value.indicator
        instance["indicator"] = serder.ListSerDer(__SubscriptionInformationsInstallationIndicatorSerDer__()).encode(indicatorValue)
        contactsValue = value.contacts
        instance["contacts"] = serder.ListSerDer(serder.STRING).encode(contactsValue)
        from netbluemind.system.api.SubscriptionInformationsMessage import SubscriptionInformationsMessage
        from netbluemind.system.api.SubscriptionInformationsMessage import __SubscriptionInformationsMessageSerDer__
        messagesValue = value.messages
        instance["messages"] = serder.ListSerDer(__SubscriptionInformationsMessageSerDer__()).encode(messagesValue)
        return instance

