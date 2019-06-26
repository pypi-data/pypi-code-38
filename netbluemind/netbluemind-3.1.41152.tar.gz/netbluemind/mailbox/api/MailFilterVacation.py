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

class MailFilterVacation :
    def __init__( self):
        self.enabled = None
        self.start = None
        self.end = None
        self.text = None
        self.subject = None
        pass

class __MailFilterVacationSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailFilterVacation()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        enabledValue = value['enabled']
        instance.enabled = serder.BOOLEAN.parse(enabledValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        startValue = value['start']
        instance.start = __BmDateTimeSerDer__().parse(startValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        endValue = value['end']
        instance.end = __BmDateTimeSerDer__().parse(endValue)
        textValue = value['text']
        instance.text = serder.STRING.parse(textValue)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        enabledValue = value.enabled
        instance["enabled"] = serder.BOOLEAN.encode(enabledValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        startValue = value.start
        instance["start"] = __BmDateTimeSerDer__().encode(startValue)
        from netbluemind.core.api.date.BmDateTime import BmDateTime
        from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
        endValue = value.end
        instance["end"] = __BmDateTimeSerDer__().encode(endValue)
        textValue = value.text
        instance["text"] = serder.STRING.encode(textValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        return instance

