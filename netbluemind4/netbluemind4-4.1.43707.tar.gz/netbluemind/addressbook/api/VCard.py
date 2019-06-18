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

class VCard :
    def __init__( self):
        self.kind = None
        self.source = None
        self.identification = None
        self.deliveryAddressing = None
        self.communications = None
        self.organizational = None
        self.explanatory = None
        self.security = None
        self.related = None
        pass

class __VCardSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCard()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardKind import VCardKind
        from netbluemind.addressbook.api.VCardKind import __VCardKindSerDer__
        kindValue = value['kind']
        instance.kind = __VCardKindSerDer__().parse(kindValue)
        sourceValue = value['source']
        instance.source = serder.STRING.parse(sourceValue)
        from netbluemind.addressbook.api.VCardIdentification import VCardIdentification
        from netbluemind.addressbook.api.VCardIdentification import __VCardIdentificationSerDer__
        identificationValue = value['identification']
        instance.identification = __VCardIdentificationSerDer__().parse(identificationValue)
        from netbluemind.addressbook.api.VCardDeliveryAddressing import VCardDeliveryAddressing
        from netbluemind.addressbook.api.VCardDeliveryAddressing import __VCardDeliveryAddressingSerDer__
        deliveryAddressingValue = value['deliveryAddressing']
        instance.deliveryAddressing = serder.ListSerDer(__VCardDeliveryAddressingSerDer__()).parse(deliveryAddressingValue)
        from netbluemind.addressbook.api.VCardCommunications import VCardCommunications
        from netbluemind.addressbook.api.VCardCommunications import __VCardCommunicationsSerDer__
        communicationsValue = value['communications']
        instance.communications = __VCardCommunicationsSerDer__().parse(communicationsValue)
        from netbluemind.addressbook.api.VCardOrganizational import VCardOrganizational
        from netbluemind.addressbook.api.VCardOrganizational import __VCardOrganizationalSerDer__
        organizationalValue = value['organizational']
        instance.organizational = __VCardOrganizationalSerDer__().parse(organizationalValue)
        from netbluemind.addressbook.api.VCardExplanatory import VCardExplanatory
        from netbluemind.addressbook.api.VCardExplanatory import __VCardExplanatorySerDer__
        explanatoryValue = value['explanatory']
        instance.explanatory = __VCardExplanatorySerDer__().parse(explanatoryValue)
        from netbluemind.addressbook.api.VCardSecurity import VCardSecurity
        from netbluemind.addressbook.api.VCardSecurity import __VCardSecuritySerDer__
        securityValue = value['security']
        instance.security = __VCardSecuritySerDer__().parse(securityValue)
        from netbluemind.addressbook.api.VCardRelated import VCardRelated
        from netbluemind.addressbook.api.VCardRelated import __VCardRelatedSerDer__
        relatedValue = value['related']
        instance.related = __VCardRelatedSerDer__().parse(relatedValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardKind import VCardKind
        from netbluemind.addressbook.api.VCardKind import __VCardKindSerDer__
        kindValue = value.kind
        instance["kind"] = __VCardKindSerDer__().encode(kindValue)
        sourceValue = value.source
        instance["source"] = serder.STRING.encode(sourceValue)
        from netbluemind.addressbook.api.VCardIdentification import VCardIdentification
        from netbluemind.addressbook.api.VCardIdentification import __VCardIdentificationSerDer__
        identificationValue = value.identification
        instance["identification"] = __VCardIdentificationSerDer__().encode(identificationValue)
        from netbluemind.addressbook.api.VCardDeliveryAddressing import VCardDeliveryAddressing
        from netbluemind.addressbook.api.VCardDeliveryAddressing import __VCardDeliveryAddressingSerDer__
        deliveryAddressingValue = value.deliveryAddressing
        instance["deliveryAddressing"] = serder.ListSerDer(__VCardDeliveryAddressingSerDer__()).encode(deliveryAddressingValue)
        from netbluemind.addressbook.api.VCardCommunications import VCardCommunications
        from netbluemind.addressbook.api.VCardCommunications import __VCardCommunicationsSerDer__
        communicationsValue = value.communications
        instance["communications"] = __VCardCommunicationsSerDer__().encode(communicationsValue)
        from netbluemind.addressbook.api.VCardOrganizational import VCardOrganizational
        from netbluemind.addressbook.api.VCardOrganizational import __VCardOrganizationalSerDer__
        organizationalValue = value.organizational
        instance["organizational"] = __VCardOrganizationalSerDer__().encode(organizationalValue)
        from netbluemind.addressbook.api.VCardExplanatory import VCardExplanatory
        from netbluemind.addressbook.api.VCardExplanatory import __VCardExplanatorySerDer__
        explanatoryValue = value.explanatory
        instance["explanatory"] = __VCardExplanatorySerDer__().encode(explanatoryValue)
        from netbluemind.addressbook.api.VCardSecurity import VCardSecurity
        from netbluemind.addressbook.api.VCardSecurity import __VCardSecuritySerDer__
        securityValue = value.security
        instance["security"] = __VCardSecuritySerDer__().encode(securityValue)
        from netbluemind.addressbook.api.VCardRelated import VCardRelated
        from netbluemind.addressbook.api.VCardRelated import __VCardRelatedSerDer__
        relatedValue = value.related
        instance["related"] = __VCardRelatedSerDer__().encode(relatedValue)
        return instance

