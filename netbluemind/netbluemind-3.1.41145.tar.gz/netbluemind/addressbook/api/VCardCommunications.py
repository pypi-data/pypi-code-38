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

class VCardCommunications :
    def __init__( self):
        self.tels = None
        self.emails = None
        self.impps = None
        self.langs = None
        pass

class __VCardCommunicationsSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardCommunications()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardCommunicationsTel import VCardCommunicationsTel
        from netbluemind.addressbook.api.VCardCommunicationsTel import __VCardCommunicationsTelSerDer__
        telsValue = value['tels']
        instance.tels = serder.ListSerDer(__VCardCommunicationsTelSerDer__()).parse(telsValue)
        from netbluemind.addressbook.api.VCardCommunicationsEmail import VCardCommunicationsEmail
        from netbluemind.addressbook.api.VCardCommunicationsEmail import __VCardCommunicationsEmailSerDer__
        emailsValue = value['emails']
        instance.emails = serder.ListSerDer(__VCardCommunicationsEmailSerDer__()).parse(emailsValue)
        from netbluemind.addressbook.api.VCardCommunicationsImpp import VCardCommunicationsImpp
        from netbluemind.addressbook.api.VCardCommunicationsImpp import __VCardCommunicationsImppSerDer__
        imppsValue = value['impps']
        instance.impps = serder.ListSerDer(__VCardCommunicationsImppSerDer__()).parse(imppsValue)
        from netbluemind.addressbook.api.VCardCommunicationsLang import VCardCommunicationsLang
        from netbluemind.addressbook.api.VCardCommunicationsLang import __VCardCommunicationsLangSerDer__
        langsValue = value['langs']
        instance.langs = serder.ListSerDer(__VCardCommunicationsLangSerDer__()).parse(langsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardCommunicationsTel import VCardCommunicationsTel
        from netbluemind.addressbook.api.VCardCommunicationsTel import __VCardCommunicationsTelSerDer__
        telsValue = value.tels
        instance["tels"] = serder.ListSerDer(__VCardCommunicationsTelSerDer__()).encode(telsValue)
        from netbluemind.addressbook.api.VCardCommunicationsEmail import VCardCommunicationsEmail
        from netbluemind.addressbook.api.VCardCommunicationsEmail import __VCardCommunicationsEmailSerDer__
        emailsValue = value.emails
        instance["emails"] = serder.ListSerDer(__VCardCommunicationsEmailSerDer__()).encode(emailsValue)
        from netbluemind.addressbook.api.VCardCommunicationsImpp import VCardCommunicationsImpp
        from netbluemind.addressbook.api.VCardCommunicationsImpp import __VCardCommunicationsImppSerDer__
        imppsValue = value.impps
        instance["impps"] = serder.ListSerDer(__VCardCommunicationsImppSerDer__()).encode(imppsValue)
        from netbluemind.addressbook.api.VCardCommunicationsLang import VCardCommunicationsLang
        from netbluemind.addressbook.api.VCardCommunicationsLang import __VCardCommunicationsLangSerDer__
        langsValue = value.langs
        instance["langs"] = serder.ListSerDer(__VCardCommunicationsLangSerDer__()).encode(langsValue)
        return instance

