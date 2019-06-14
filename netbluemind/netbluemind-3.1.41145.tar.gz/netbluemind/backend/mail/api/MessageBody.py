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

class MessageBody :
    def __init__( self):
        self.guid = None
        self.subject = None
        self.smartAttach = None
        self.date = None
        self.size = None
        self.headers = None
        self.recipients = None
        self.structure = None
        self.preview = None
        self.bodyVersion = None
        pass

class __MessageBodySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MessageBody()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        guidValue = value['guid']
        instance.guid = serder.STRING.parse(guidValue)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        smartAttachValue = value['smartAttach']
        instance.smartAttach = serder.BOOLEAN.parse(smartAttachValue)
        dateValue = value['date']
        instance.date = serder.DATE.parse(dateValue)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        from netbluemind.backend.mail.api.MessageBodyHeader import MessageBodyHeader
        from netbluemind.backend.mail.api.MessageBodyHeader import __MessageBodyHeaderSerDer__
        headersValue = value['headers']
        instance.headers = serder.ListSerDer(__MessageBodyHeaderSerDer__()).parse(headersValue)
        from netbluemind.backend.mail.api.MessageBodyRecipient import MessageBodyRecipient
        from netbluemind.backend.mail.api.MessageBodyRecipient import __MessageBodyRecipientSerDer__
        recipientsValue = value['recipients']
        instance.recipients = serder.ListSerDer(__MessageBodyRecipientSerDer__()).parse(recipientsValue)
        from netbluemind.backend.mail.api.MessageBodyPart import MessageBodyPart
        from netbluemind.backend.mail.api.MessageBodyPart import __MessageBodyPartSerDer__
        structureValue = value['structure']
        instance.structure = __MessageBodyPartSerDer__().parse(structureValue)
        previewValue = value['preview']
        instance.preview = serder.STRING.parse(previewValue)
        bodyVersionValue = value['bodyVersion']
        instance.bodyVersion = serder.INT.parse(bodyVersionValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        guidValue = value.guid
        instance["guid"] = serder.STRING.encode(guidValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        smartAttachValue = value.smartAttach
        instance["smartAttach"] = serder.BOOLEAN.encode(smartAttachValue)
        dateValue = value.date
        instance["date"] = serder.DATE.encode(dateValue)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        from netbluemind.backend.mail.api.MessageBodyHeader import MessageBodyHeader
        from netbluemind.backend.mail.api.MessageBodyHeader import __MessageBodyHeaderSerDer__
        headersValue = value.headers
        instance["headers"] = serder.ListSerDer(__MessageBodyHeaderSerDer__()).encode(headersValue)
        from netbluemind.backend.mail.api.MessageBodyRecipient import MessageBodyRecipient
        from netbluemind.backend.mail.api.MessageBodyRecipient import __MessageBodyRecipientSerDer__
        recipientsValue = value.recipients
        instance["recipients"] = serder.ListSerDer(__MessageBodyRecipientSerDer__()).encode(recipientsValue)
        from netbluemind.backend.mail.api.MessageBodyPart import MessageBodyPart
        from netbluemind.backend.mail.api.MessageBodyPart import __MessageBodyPartSerDer__
        structureValue = value.structure
        instance["structure"] = __MessageBodyPartSerDer__().encode(structureValue)
        previewValue = value.preview
        instance["preview"] = serder.STRING.encode(previewValue)
        bodyVersionValue = value.bodyVersion
        instance["bodyVersion"] = serder.INT.encode(bodyVersionValue)
        return instance

