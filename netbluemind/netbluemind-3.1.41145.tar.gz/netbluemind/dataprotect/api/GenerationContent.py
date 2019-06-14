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

class GenerationContent :
    def __init__( self):
        self.generationId = None
        self.domains = None
        self.servers = None
        self.entries = None
        self.capabilities = None
        pass

class __GenerationContentSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = GenerationContent()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        generationIdValue = value['generationId']
        instance.generationId = serder.INT.parse(generationIdValue)
        from netbluemind.domain.api.Domain import Domain
        from netbluemind.domain.api.Domain import __DomainSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        domainsValue = value['domains']
        instance.domains = serder.ListSerDer(__ItemValueSerDer__(__DomainSerDer__())).parse(domainsValue)
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        serversValue = value['servers']
        instance.servers = serder.ListSerDer(__ItemValueSerDer__(__ServerSerDer__())).parse(serversValue)
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        entriesValue = value['entries']
        instance.entries = serder.ListSerDer(__ItemValueSerDer__(__DirEntrySerDer__())).parse(entriesValue)
        from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
        from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
        capabilitiesValue = value['capabilities']
        instance.capabilities = serder.ListSerDer(__RestoreOperationSerDer__()).parse(capabilitiesValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        generationIdValue = value.generationId
        instance["generationId"] = serder.INT.encode(generationIdValue)
        from netbluemind.domain.api.Domain import Domain
        from netbluemind.domain.api.Domain import __DomainSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        domainsValue = value.domains
        instance["domains"] = serder.ListSerDer(__ItemValueSerDer__(__DomainSerDer__())).encode(domainsValue)
        from netbluemind.server.api.Server import Server
        from netbluemind.server.api.Server import __ServerSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        serversValue = value.servers
        instance["servers"] = serder.ListSerDer(__ItemValueSerDer__(__ServerSerDer__())).encode(serversValue)
        from netbluemind.directory.api.DirEntry import DirEntry
        from netbluemind.directory.api.DirEntry import __DirEntrySerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        entriesValue = value.entries
        instance["entries"] = serder.ListSerDer(__ItemValueSerDer__(__DirEntrySerDer__())).encode(entriesValue)
        from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
        from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
        capabilitiesValue = value.capabilities
        instance["capabilities"] = serder.ListSerDer(__RestoreOperationSerDer__()).encode(capabilitiesValue)
        return instance

