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

class MessageSearchResult :
    def __init__( self):
        self.containerUid = None
        self.itemId = None
        self.subject = None
        self.size = None
        self.messageClass = None
        self.date = None
        self.from_ = None
        self.to = None
        self.seen = None
        self.flagged = None
        self.hasAttachment = None
        self.preview = None
        pass

class __MessageSearchResultSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MessageSearchResult()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        containerUidValue = value['containerUid']
        instance.containerUid = serder.STRING.parse(containerUidValue)
        itemIdValue = value['itemId']
        instance.itemId = serder.INT.parse(itemIdValue)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        messageClassValue = value['messageClass']
        instance.messageClass = serder.STRING.parse(messageClassValue)
        dateValue = value['date']
        instance.date = serder.DATE.parse(dateValue)
        from netbluemind.backend.mail.api.MessageSearchResultMbox import MessageSearchResultMbox
        from netbluemind.backend.mail.api.MessageSearchResultMbox import __MessageSearchResultMboxSerDer__
        from_Value = value['from']
        instance.from_ = __MessageSearchResultMboxSerDer__().parse(from_Value)
        from netbluemind.backend.mail.api.MessageSearchResultMbox import MessageSearchResultMbox
        from netbluemind.backend.mail.api.MessageSearchResultMbox import __MessageSearchResultMboxSerDer__
        toValue = value['to']
        instance.to = __MessageSearchResultMboxSerDer__().parse(toValue)
        seenValue = value['seen']
        instance.seen = serder.BOOLEAN.parse(seenValue)
        flaggedValue = value['flagged']
        instance.flagged = serder.BOOLEAN.parse(flaggedValue)
        hasAttachmentValue = value['hasAttachment']
        instance.hasAttachment = serder.BOOLEAN.parse(hasAttachmentValue)
        previewValue = value['preview']
        instance.preview = serder.STRING.parse(previewValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        containerUidValue = value.containerUid
        instance["containerUid"] = serder.STRING.encode(containerUidValue)
        itemIdValue = value.itemId
        instance["itemId"] = serder.INT.encode(itemIdValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        messageClassValue = value.messageClass
        instance["messageClass"] = serder.STRING.encode(messageClassValue)
        dateValue = value.date
        instance["date"] = serder.DATE.encode(dateValue)
        from netbluemind.backend.mail.api.MessageSearchResultMbox import MessageSearchResultMbox
        from netbluemind.backend.mail.api.MessageSearchResultMbox import __MessageSearchResultMboxSerDer__
        from_Value = value.from_
        instance["from"] = __MessageSearchResultMboxSerDer__().encode(from_Value)
        from netbluemind.backend.mail.api.MessageSearchResultMbox import MessageSearchResultMbox
        from netbluemind.backend.mail.api.MessageSearchResultMbox import __MessageSearchResultMboxSerDer__
        toValue = value.to
        instance["to"] = __MessageSearchResultMboxSerDer__().encode(toValue)
        seenValue = value.seen
        instance["seen"] = serder.BOOLEAN.encode(seenValue)
        flaggedValue = value.flagged
        instance["flagged"] = serder.BOOLEAN.encode(flaggedValue)
        hasAttachmentValue = value.hasAttachment
        instance["hasAttachment"] = serder.BOOLEAN.encode(hasAttachmentValue)
        previewValue = value.preview
        instance["preview"] = serder.STRING.encode(previewValue)
        return instance

