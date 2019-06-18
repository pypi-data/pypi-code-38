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

class DirEntryQuery :
    def __init__( self):
        self.order = None
        self.nameFilter = None
        self.hiddenFilter = None
        self.emailFilter = None
        self.nameOrEmailFilter = None
        self.stateFilter = None
        self.systemFilter = None
        self.kindsFilter = None
        self.entries = None
        self.accountTypeFilter = None
        self.from_ = None
        self.size = None
        self.entryUidFilter = None
        self.onlyManagable = None
        pass

class __DirEntryQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = DirEntryQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.directory.api.DirEntryQueryOrder import DirEntryQueryOrder
        from netbluemind.directory.api.DirEntryQueryOrder import __DirEntryQueryOrderSerDer__
        orderValue = value['order']
        instance.order = __DirEntryQueryOrderSerDer__().parse(orderValue)
        nameFilterValue = value['nameFilter']
        instance.nameFilter = serder.STRING.parse(nameFilterValue)
        hiddenFilterValue = value['hiddenFilter']
        instance.hiddenFilter = serder.BOOLEAN.parse(hiddenFilterValue)
        emailFilterValue = value['emailFilter']
        instance.emailFilter = serder.STRING.parse(emailFilterValue)
        nameOrEmailFilterValue = value['nameOrEmailFilter']
        instance.nameOrEmailFilter = serder.STRING.parse(nameOrEmailFilterValue)
        from netbluemind.directory.api.DirEntryQueryStateFilter import DirEntryQueryStateFilter
        from netbluemind.directory.api.DirEntryQueryStateFilter import __DirEntryQueryStateFilterSerDer__
        stateFilterValue = value['stateFilter']
        instance.stateFilter = __DirEntryQueryStateFilterSerDer__().parse(stateFilterValue)
        systemFilterValue = value['systemFilter']
        instance.systemFilter = serder.BOOLEAN.parse(systemFilterValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        kindsFilterValue = value['kindsFilter']
        instance.kindsFilter = serder.ListSerDer(__BaseDirEntryKindSerDer__()).parse(kindsFilterValue)
        entriesValue = value['entries']
        instance.entries = serder.ListSerDer(serder.STRING).parse(entriesValue)
        from netbluemind.directory.api.BaseDirEntryAccountType import BaseDirEntryAccountType
        from netbluemind.directory.api.BaseDirEntryAccountType import __BaseDirEntryAccountTypeSerDer__
        accountTypeFilterValue = value['accountTypeFilter']
        instance.accountTypeFilter = __BaseDirEntryAccountTypeSerDer__().parse(accountTypeFilterValue)
        from_Value = value['from']
        instance.from_ = serder.INT.parse(from_Value)
        sizeValue = value['size']
        instance.size = serder.INT.parse(sizeValue)
        entryUidFilterValue = value['entryUidFilter']
        instance.entryUidFilter = serder.ListSerDer(serder.STRING).parse(entryUidFilterValue)
        onlyManagableValue = value['onlyManagable']
        instance.onlyManagable = serder.BOOLEAN.parse(onlyManagableValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.directory.api.DirEntryQueryOrder import DirEntryQueryOrder
        from netbluemind.directory.api.DirEntryQueryOrder import __DirEntryQueryOrderSerDer__
        orderValue = value.order
        instance["order"] = __DirEntryQueryOrderSerDer__().encode(orderValue)
        nameFilterValue = value.nameFilter
        instance["nameFilter"] = serder.STRING.encode(nameFilterValue)
        hiddenFilterValue = value.hiddenFilter
        instance["hiddenFilter"] = serder.BOOLEAN.encode(hiddenFilterValue)
        emailFilterValue = value.emailFilter
        instance["emailFilter"] = serder.STRING.encode(emailFilterValue)
        nameOrEmailFilterValue = value.nameOrEmailFilter
        instance["nameOrEmailFilter"] = serder.STRING.encode(nameOrEmailFilterValue)
        from netbluemind.directory.api.DirEntryQueryStateFilter import DirEntryQueryStateFilter
        from netbluemind.directory.api.DirEntryQueryStateFilter import __DirEntryQueryStateFilterSerDer__
        stateFilterValue = value.stateFilter
        instance["stateFilter"] = __DirEntryQueryStateFilterSerDer__().encode(stateFilterValue)
        systemFilterValue = value.systemFilter
        instance["systemFilter"] = serder.BOOLEAN.encode(systemFilterValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        kindsFilterValue = value.kindsFilter
        instance["kindsFilter"] = serder.ListSerDer(__BaseDirEntryKindSerDer__()).encode(kindsFilterValue)
        entriesValue = value.entries
        instance["entries"] = serder.ListSerDer(serder.STRING).encode(entriesValue)
        from netbluemind.directory.api.BaseDirEntryAccountType import BaseDirEntryAccountType
        from netbluemind.directory.api.BaseDirEntryAccountType import __BaseDirEntryAccountTypeSerDer__
        accountTypeFilterValue = value.accountTypeFilter
        instance["accountTypeFilter"] = __BaseDirEntryAccountTypeSerDer__().encode(accountTypeFilterValue)
        from_Value = value.from_
        instance["from"] = serder.INT.encode(from_Value)
        sizeValue = value.size
        instance["size"] = serder.INT.encode(sizeValue)
        entryUidFilterValue = value.entryUidFilter
        instance["entryUidFilter"] = serder.ListSerDer(serder.STRING).encode(entryUidFilterValue)
        onlyManagableValue = value.onlyManagable
        instance["onlyManagable"] = serder.BOOLEAN.encode(onlyManagableValue)
        return instance

