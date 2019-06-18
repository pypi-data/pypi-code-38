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

class VCardIdentification :
    def __init__( self):
        self.formatedName = None
        self.name = None
        self.nickname = None
        self.photo = None
        self.birthday = None
        self.anniversary = None
        self.gender = None
        pass

class __VCardIdentificationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardIdentification()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCardIdentificationFormatedName import VCardIdentificationFormatedName
        from netbluemind.addressbook.api.VCardIdentificationFormatedName import __VCardIdentificationFormatedNameSerDer__
        formatedNameValue = value['formatedName']
        instance.formatedName = __VCardIdentificationFormatedNameSerDer__().parse(formatedNameValue)
        from netbluemind.addressbook.api.VCardIdentificationName import VCardIdentificationName
        from netbluemind.addressbook.api.VCardIdentificationName import __VCardIdentificationNameSerDer__
        nameValue = value['name']
        instance.name = __VCardIdentificationNameSerDer__().parse(nameValue)
        from netbluemind.addressbook.api.VCardIdentificationNickname import VCardIdentificationNickname
        from netbluemind.addressbook.api.VCardIdentificationNickname import __VCardIdentificationNicknameSerDer__
        nicknameValue = value['nickname']
        instance.nickname = __VCardIdentificationNicknameSerDer__().parse(nicknameValue)
        photoValue = value['photo']
        instance.photo = serder.BOOLEAN.parse(photoValue)
        birthdayValue = value['birthday']
        instance.birthday = serder.DATE.parse(birthdayValue)
        anniversaryValue = value['anniversary']
        instance.anniversary = serder.DATE.parse(anniversaryValue)
        from netbluemind.addressbook.api.VCardIdentificationGender import VCardIdentificationGender
        from netbluemind.addressbook.api.VCardIdentificationGender import __VCardIdentificationGenderSerDer__
        genderValue = value['gender']
        instance.gender = __VCardIdentificationGenderSerDer__().parse(genderValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.addressbook.api.VCardIdentificationFormatedName import VCardIdentificationFormatedName
        from netbluemind.addressbook.api.VCardIdentificationFormatedName import __VCardIdentificationFormatedNameSerDer__
        formatedNameValue = value.formatedName
        instance["formatedName"] = __VCardIdentificationFormatedNameSerDer__().encode(formatedNameValue)
        from netbluemind.addressbook.api.VCardIdentificationName import VCardIdentificationName
        from netbluemind.addressbook.api.VCardIdentificationName import __VCardIdentificationNameSerDer__
        nameValue = value.name
        instance["name"] = __VCardIdentificationNameSerDer__().encode(nameValue)
        from netbluemind.addressbook.api.VCardIdentificationNickname import VCardIdentificationNickname
        from netbluemind.addressbook.api.VCardIdentificationNickname import __VCardIdentificationNicknameSerDer__
        nicknameValue = value.nickname
        instance["nickname"] = __VCardIdentificationNicknameSerDer__().encode(nicknameValue)
        photoValue = value.photo
        instance["photo"] = serder.BOOLEAN.encode(photoValue)
        birthdayValue = value.birthday
        instance["birthday"] = serder.DATE.encode(birthdayValue)
        anniversaryValue = value.anniversary
        instance["anniversary"] = serder.DATE.encode(anniversaryValue)
        from netbluemind.addressbook.api.VCardIdentificationGender import VCardIdentificationGender
        from netbluemind.addressbook.api.VCardIdentificationGender import __VCardIdentificationGenderSerDer__
        genderValue = value.gender
        instance["gender"] = __VCardIdentificationGenderSerDer__().encode(genderValue)
        return instance

