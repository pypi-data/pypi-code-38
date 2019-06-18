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

class MessageBodyPart :
    def __init__( self):
        self.mime = None
        self.address = None
        self.encoding = None
        self.charset = None
        self.fileName = None
        self.headers = None
        self.contentId = None
        self.children = None
        self.size = None
        self.dispositionType = None
        pass

class __MessageBodyPartSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MessageBodyPart()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        mimeValue = value['mime']
        instance.mime = serder.STRING.parse(mimeValue)
        addressValue = value['address']
        instance.address = serder.STRING.parse(addressValue)
        encodingValue = value['encoding']
        instance.encoding = serder.STRING.parse(encodingValue)
        charsetValue = value['charset']
        instance.charset = serder.STRING.parse(charsetValue)
        fileNameValue = value['fileName']
        instance.fileName = serder.STRING.parse(fileNameValue)
        from netbluemind.backend.mail.api.MessageBodyHeader import MessageBodyHeader
        from netbluemind.backend.mail.api.MessageBodyHeader import __MessageBodyHeaderSerDer__
        headersValue = value['headers']
        instance.headers = serder.ListSerDer(__MessageBodyHeaderSerDer__()).parse(headersValue)
        contentIdValue = value['contentId']
        instance.contentId = serder.STRING.parse(contentIdValue)
        from netbluemind.backend.mail.api.MessageBodyPart import MessageBodyPart
        from netbluemind.backend.mail.api.MessageBodyPart import __MessageBodyPartSerDer__
        childrenValue = value['children']
        instance.children = serder.ListSerDer(__MessageBodyPartSerDer__()).parse(childrenValue)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        from netbluemind.backend.mail.api.DispositionType import DispositionType
        from netbluemind.backend.mail.api.DispositionType import __DispositionTypeSerDer__
        dispositionTypeValue = value['dispositionType']
        instance.dispositionType = __DispositionTypeSerDer__().parse(dispositionTypeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        mimeValue = value.mime
        instance["mime"] = serder.STRING.encode(mimeValue)
        addressValue = value.address
        instance["address"] = serder.STRING.encode(addressValue)
        encodingValue = value.encoding
        instance["encoding"] = serder.STRING.encode(encodingValue)
        charsetValue = value.charset
        instance["charset"] = serder.STRING.encode(charsetValue)
        fileNameValue = value.fileName
        instance["fileName"] = serder.STRING.encode(fileNameValue)
        from netbluemind.backend.mail.api.MessageBodyHeader import MessageBodyHeader
        from netbluemind.backend.mail.api.MessageBodyHeader import __MessageBodyHeaderSerDer__
        headersValue = value.headers
        instance["headers"] = serder.ListSerDer(__MessageBodyHeaderSerDer__()).encode(headersValue)
        contentIdValue = value.contentId
        instance["contentId"] = serder.STRING.encode(contentIdValue)
        from netbluemind.backend.mail.api.MessageBodyPart import MessageBodyPart
        from netbluemind.backend.mail.api.MessageBodyPart import __MessageBodyPartSerDer__
        childrenValue = value.children
        instance["children"] = serder.ListSerDer(__MessageBodyPartSerDer__()).encode(childrenValue)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        from netbluemind.backend.mail.api.DispositionType import DispositionType
        from netbluemind.backend.mail.api.DispositionType import __DispositionTypeSerDer__
        dispositionTypeValue = value.dispositionType
        instance["dispositionType"] = __DispositionTypeSerDer__().encode(dispositionTypeValue)
        return instance

