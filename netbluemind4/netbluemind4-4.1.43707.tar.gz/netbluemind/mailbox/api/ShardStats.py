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

class ShardStats :
    def __init__( self):
        self.indexName = None
        self.mailboxes = None
        self.topMailbox = None
        self.docCount = None
        self.state = None
        self.size = None
        pass

class __ShardStatsSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ShardStats()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        indexNameValue = value['indexName']
        instance.indexName = serder.STRING.parse(indexNameValue)
        mailboxesValue = value['mailboxes']
        instance.mailboxes = serder.SetSerDer(serder.STRING).parse(mailboxesValue)
        from netbluemind.mailbox.api.ShardStatsMailboxStats import ShardStatsMailboxStats
        from netbluemind.mailbox.api.ShardStatsMailboxStats import __ShardStatsMailboxStatsSerDer__
        topMailboxValue = value['topMailbox']
        instance.topMailbox = serder.ListSerDer(__ShardStatsMailboxStatsSerDer__()).parse(topMailboxValue)
        docCountValue = value['docCount']
        instance.docCount = serder.LONG.parse(docCountValue)
        from netbluemind.mailbox.api.ShardStatsState import ShardStatsState
        from netbluemind.mailbox.api.ShardStatsState import __ShardStatsStateSerDer__
        stateValue = value['state']
        instance.state = __ShardStatsStateSerDer__().parse(stateValue)
        sizeValue = value['size']
        instance.size = serder.LONG.parse(sizeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        indexNameValue = value.indexName
        instance["indexName"] = serder.STRING.encode(indexNameValue)
        mailboxesValue = value.mailboxes
        instance["mailboxes"] = serder.SetSerDer(serder.STRING).encode(mailboxesValue)
        from netbluemind.mailbox.api.ShardStatsMailboxStats import ShardStatsMailboxStats
        from netbluemind.mailbox.api.ShardStatsMailboxStats import __ShardStatsMailboxStatsSerDer__
        topMailboxValue = value.topMailbox
        instance["topMailbox"] = serder.ListSerDer(__ShardStatsMailboxStatsSerDer__()).encode(topMailboxValue)
        docCountValue = value.docCount
        instance["docCount"] = serder.LONG.encode(docCountValue)
        from netbluemind.mailbox.api.ShardStatsState import ShardStatsState
        from netbluemind.mailbox.api.ShardStatsState import __ShardStatsStateSerDer__
        stateValue = value.state
        instance["state"] = __ShardStatsStateSerDer__().encode(stateValue)
        sizeValue = value.size
        instance["size"] = serder.LONG.encode(sizeValue)
        return instance

