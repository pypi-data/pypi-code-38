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

class RoleDescriptor :
    def __init__( self):
        self.id = None
        self.parentRoleId = None
        self.categoryId = None
        self.label = None
        self.description = None
        self.selfPromote = None
        self.dirEntryPromote = None
        self.dirEntryKind = None
        self.siblingRole = None
        self.childsRole = None
        self.visible = None
        self.delegable = None
        self.containerRoles = None
        self.priority = None
        pass

class __RoleDescriptorSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = RoleDescriptor()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        idValue = value['id']
        instance.id = serder.STRING.parse(idValue)
        parentRoleIdValue = value['parentRoleId']
        instance.parentRoleId = serder.STRING.parse(parentRoleIdValue)
        categoryIdValue = value['categoryId']
        instance.categoryId = serder.STRING.parse(categoryIdValue)
        labelValue = value['label']
        instance.label = serder.STRING.parse(labelValue)
        descriptionValue = value['description']
        instance.description = serder.STRING.parse(descriptionValue)
        selfPromoteValue = value['selfPromote']
        instance.selfPromote = serder.BOOLEAN.parse(selfPromoteValue)
        dirEntryPromoteValue = value['dirEntryPromote']
        instance.dirEntryPromote = serder.BOOLEAN.parse(dirEntryPromoteValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        dirEntryKindValue = value['dirEntryKind']
        instance.dirEntryKind = __BaseDirEntryKindSerDer__().parse(dirEntryKindValue)
        siblingRoleValue = value['siblingRole']
        instance.siblingRole = serder.STRING.parse(siblingRoleValue)
        childsRoleValue = value['childsRole']
        instance.childsRole = serder.SetSerDer(serder.STRING).parse(childsRoleValue)
        visibleValue = value['visible']
        instance.visible = serder.BOOLEAN.parse(visibleValue)
        delegableValue = value['delegable']
        instance.delegable = serder.BOOLEAN.parse(delegableValue)
        containerRolesValue = value['containerRoles']
        instance.containerRoles = serder.SetSerDer(serder.STRING).parse(containerRolesValue)
        priorityValue = value['priority']
        instance.priority = serder.INT.parse(priorityValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        idValue = value.id
        instance["id"] = serder.STRING.encode(idValue)
        parentRoleIdValue = value.parentRoleId
        instance["parentRoleId"] = serder.STRING.encode(parentRoleIdValue)
        categoryIdValue = value.categoryId
        instance["categoryId"] = serder.STRING.encode(categoryIdValue)
        labelValue = value.label
        instance["label"] = serder.STRING.encode(labelValue)
        descriptionValue = value.description
        instance["description"] = serder.STRING.encode(descriptionValue)
        selfPromoteValue = value.selfPromote
        instance["selfPromote"] = serder.BOOLEAN.encode(selfPromoteValue)
        dirEntryPromoteValue = value.dirEntryPromote
        instance["dirEntryPromote"] = serder.BOOLEAN.encode(dirEntryPromoteValue)
        from netbluemind.directory.api.BaseDirEntryKind import BaseDirEntryKind
        from netbluemind.directory.api.BaseDirEntryKind import __BaseDirEntryKindSerDer__
        dirEntryKindValue = value.dirEntryKind
        instance["dirEntryKind"] = __BaseDirEntryKindSerDer__().encode(dirEntryKindValue)
        siblingRoleValue = value.siblingRole
        instance["siblingRole"] = serder.STRING.encode(siblingRoleValue)
        childsRoleValue = value.childsRole
        instance["childsRole"] = serder.SetSerDer(serder.STRING).encode(childsRoleValue)
        visibleValue = value.visible
        instance["visible"] = serder.BOOLEAN.encode(visibleValue)
        delegableValue = value.delegable
        instance["delegable"] = serder.BOOLEAN.encode(delegableValue)
        containerRolesValue = value.containerRoles
        instance["containerRoles"] = serder.SetSerDer(serder.STRING).encode(containerRolesValue)
        priorityValue = value.priority
        instance["priority"] = serder.INT.encode(priorityValue)
        return instance

