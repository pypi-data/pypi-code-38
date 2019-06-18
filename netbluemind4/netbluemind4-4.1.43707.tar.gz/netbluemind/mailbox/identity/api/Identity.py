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

class Identity :
    def __init__( self):
        self.email = None
        self.format = None
        self.signature = None
        self.displayname = None
        self.name = None
        self.isDefault = None
        self.sentFolder = None
        pass

class __IdentitySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Identity()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        from netbluemind.mailbox.identity.api.SignatureFormat import SignatureFormat
        from netbluemind.mailbox.identity.api.SignatureFormat import __SignatureFormatSerDer__
        formatValue = value['format']
        instance.format = __SignatureFormatSerDer__().parse(formatValue)
        signatureValue = value['signature']
        instance.signature = serder.STRING.parse(signatureValue)
        displaynameValue = value['displayname']
        instance.displayname = serder.STRING.parse(displaynameValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        isDefaultValue = value['isDefault']
        instance.isDefault = serder.BOOLEAN.parse(isDefaultValue)
        sentFolderValue = value['sentFolder']
        instance.sentFolder = serder.STRING.parse(sentFolderValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        from netbluemind.mailbox.identity.api.SignatureFormat import SignatureFormat
        from netbluemind.mailbox.identity.api.SignatureFormat import __SignatureFormatSerDer__
        formatValue = value.format
        instance["format"] = __SignatureFormatSerDer__().encode(formatValue)
        signatureValue = value.signature
        instance["signature"] = serder.STRING.encode(signatureValue)
        displaynameValue = value.displayname
        instance["displayname"] = serder.STRING.encode(displaynameValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        isDefaultValue = value.isDefault
        instance["isDefault"] = serder.BOOLEAN.encode(isDefaultValue)
        sentFolderValue = value.sentFolder
        instance["sentFolder"] = serder.STRING.encode(sentFolderValue)
        return instance

