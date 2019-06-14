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

class IdentityDescription :
    def __init__( self):
        self.mbox = None
        self.id = None
        self.email = None
        self.name = None
        self.isDefault = None
        self.displayname = None
        self.signature = None
        self.mboxName = None
        pass

class __IdentityDescriptionSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = IdentityDescription()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        mboxValue = value['mbox']
        instance.mbox = serder.STRING.parse(mboxValue)
        idValue = value['id']
        instance.id = serder.STRING.parse(idValue)
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        isDefaultValue = value['isDefault']
        instance.isDefault = serder.BOOLEAN.parse(isDefaultValue)
        displaynameValue = value['displayname']
        instance.displayname = serder.STRING.parse(displaynameValue)
        signatureValue = value['signature']
        instance.signature = serder.STRING.parse(signatureValue)
        mboxNameValue = value['mboxName']
        instance.mboxName = serder.STRING.parse(mboxNameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        mboxValue = value.mbox
        instance["mbox"] = serder.STRING.encode(mboxValue)
        idValue = value.id
        instance["id"] = serder.STRING.encode(idValue)
        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        isDefaultValue = value.isDefault
        instance["isDefault"] = serder.BOOLEAN.encode(isDefaultValue)
        displaynameValue = value.displayname
        instance["displayname"] = serder.STRING.encode(displaynameValue)
        signatureValue = value.signature
        instance["signature"] = serder.STRING.encode(signatureValue)
        mboxNameValue = value.mboxName
        instance["mboxName"] = serder.STRING.encode(mboxNameValue)
        return instance

