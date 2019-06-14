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

class AccessControlEntry :
    def __init__( self):
        self.subject = None
        self.verb = None
        pass

class __AccessControlEntrySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = AccessControlEntry()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbValue = value['verb']
        instance.verb = __VerbSerDer__().parse(verbValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        from netbluemind.core.container.model.acl.Verb import Verb
        from netbluemind.core.container.model.acl.Verb import __VerbSerDer__
        verbValue = value.verb
        instance["verb"] = __VerbSerDer__().encode(verbValue)
        return instance

