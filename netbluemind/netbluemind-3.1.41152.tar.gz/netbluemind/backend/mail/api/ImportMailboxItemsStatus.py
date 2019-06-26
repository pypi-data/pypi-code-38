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

class ImportMailboxItemsStatus :
    def __init__( self):
        self.doneIds = None
        self.status = None
        pass

class __ImportMailboxItemsStatusSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ImportMailboxItemsStatus()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportedMailboxItem import ImportMailboxItemsStatusImportedMailboxItem
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportedMailboxItem import __ImportMailboxItemsStatusImportedMailboxItemSerDer__
        doneIdsValue = value['doneIds']
        instance.doneIds = serder.ListSerDer(__ImportMailboxItemsStatusImportedMailboxItemSerDer__()).parse(doneIdsValue)
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportStatus import ImportMailboxItemsStatusImportStatus
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportStatus import __ImportMailboxItemsStatusImportStatusSerDer__
        statusValue = value['status']
        instance.status = __ImportMailboxItemsStatusImportStatusSerDer__().parse(statusValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportedMailboxItem import ImportMailboxItemsStatusImportedMailboxItem
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportedMailboxItem import __ImportMailboxItemsStatusImportedMailboxItemSerDer__
        doneIdsValue = value.doneIds
        instance["doneIds"] = serder.ListSerDer(__ImportMailboxItemsStatusImportedMailboxItemSerDer__()).encode(doneIdsValue)
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportStatus import ImportMailboxItemsStatusImportStatus
        from netbluemind.backend.mail.api.ImportMailboxItemsStatusImportStatus import __ImportMailboxItemsStatusImportStatusSerDer__
        statusValue = value.status
        instance["status"] = __ImportMailboxItemsStatusImportStatusSerDer__().encode(statusValue)
        return instance

