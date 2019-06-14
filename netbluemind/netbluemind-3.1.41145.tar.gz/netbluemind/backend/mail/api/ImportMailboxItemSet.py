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

class ImportMailboxItemSet :
    def __init__( self):
        self.mailboxFolderId = None
        self.ids = None
        self.expectedIds = None
        self.deleteFromSource = None
        pass

class __ImportMailboxItemSetSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ImportMailboxItemSet()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        mailboxFolderIdValue = value['mailboxFolderId']
        instance.mailboxFolderId = serder.LONG.parse(mailboxFolderIdValue)
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import ImportMailboxItemSetMailboxItemId
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import __ImportMailboxItemSetMailboxItemIdSerDer__
        idsValue = value['ids']
        instance.ids = serder.ListSerDer(__ImportMailboxItemSetMailboxItemIdSerDer__()).parse(idsValue)
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import ImportMailboxItemSetMailboxItemId
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import __ImportMailboxItemSetMailboxItemIdSerDer__
        expectedIdsValue = value['expectedIds']
        instance.expectedIds = serder.ListSerDer(__ImportMailboxItemSetMailboxItemIdSerDer__()).parse(expectedIdsValue)
        deleteFromSourceValue = value['deleteFromSource']
        instance.deleteFromSource = serder.BOOLEAN.parse(deleteFromSourceValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        mailboxFolderIdValue = value.mailboxFolderId
        instance["mailboxFolderId"] = serder.LONG.encode(mailboxFolderIdValue)
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import ImportMailboxItemSetMailboxItemId
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import __ImportMailboxItemSetMailboxItemIdSerDer__
        idsValue = value.ids
        instance["ids"] = serder.ListSerDer(__ImportMailboxItemSetMailboxItemIdSerDer__()).encode(idsValue)
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import ImportMailboxItemSetMailboxItemId
        from netbluemind.backend.mail.api.ImportMailboxItemSetMailboxItemId import __ImportMailboxItemSetMailboxItemIdSerDer__
        expectedIdsValue = value.expectedIds
        instance["expectedIds"] = serder.ListSerDer(__ImportMailboxItemSetMailboxItemIdSerDer__()).encode(expectedIdsValue)
        deleteFromSourceValue = value.deleteFromSource
        instance["deleteFromSource"] = serder.BOOLEAN.encode(deleteFromSourceValue)
        return instance

