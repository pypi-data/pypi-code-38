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

class VCardOrganizational :
    def __init__( self):
        self.title = None
        self.role = None
        self.org = None
        self.member = None
        pass

class __VCardOrganizationalSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VCardOrganizational()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        titleValue = value['title']
        instance.title = serder.STRING.parse(titleValue)
        roleValue = value['role']
        instance.role = serder.STRING.parse(roleValue)
        from netbluemind.addressbook.api.VCardOrganizationalOrg import VCardOrganizationalOrg
        from netbluemind.addressbook.api.VCardOrganizationalOrg import __VCardOrganizationalOrgSerDer__
        orgValue = value['org']
        instance.org = __VCardOrganizationalOrgSerDer__().parse(orgValue)
        from netbluemind.addressbook.api.VCardOrganizationalMember import VCardOrganizationalMember
        from netbluemind.addressbook.api.VCardOrganizationalMember import __VCardOrganizationalMemberSerDer__
        memberValue = value['member']
        instance.member = serder.ListSerDer(__VCardOrganizationalMemberSerDer__()).parse(memberValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        titleValue = value.title
        instance["title"] = serder.STRING.encode(titleValue)
        roleValue = value.role
        instance["role"] = serder.STRING.encode(roleValue)
        from netbluemind.addressbook.api.VCardOrganizationalOrg import VCardOrganizationalOrg
        from netbluemind.addressbook.api.VCardOrganizationalOrg import __VCardOrganizationalOrgSerDer__
        orgValue = value.org
        instance["org"] = __VCardOrganizationalOrgSerDer__().encode(orgValue)
        from netbluemind.addressbook.api.VCardOrganizationalMember import VCardOrganizationalMember
        from netbluemind.addressbook.api.VCardOrganizationalMember import __VCardOrganizationalMemberSerDer__
        memberValue = value.member
        instance["member"] = serder.ListSerDer(__VCardOrganizationalMemberSerDer__()).encode(memberValue)
        return instance

