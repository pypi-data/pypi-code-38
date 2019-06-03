# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class BuildingsAndOrganizations(Model):
    """BuildingsAndOrganizations.

    :param view:
    :type view: bool
    :param create:
    :type create: bool
    :param edit:
    :type edit: bool
    :param delete:
    :type delete: bool
    :param permission_id:
    :type permission_id: int
    :param permission_code:
    :type permission_code: str
    :param permission_name:
    :type permission_name: str
    :param description:
    :type description: str
    :param permission_category_name:
    :type permission_category_name: str
    :param is_licensed:
    :type is_licensed: bool
    """

    _attribute_map = {
        'view': {'key': 'view', 'type': 'bool'},
        'create': {'key': 'create', 'type': 'bool'},
        'edit': {'key': 'edit', 'type': 'bool'},
        'delete': {'key': 'delete', 'type': 'bool'},
        'permission_id': {'key': 'permissionId', 'type': 'int'},
        'permission_code': {'key': 'permissionCode', 'type': 'str'},
        'permission_name': {'key': 'permissionName', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'permission_category_name': {'key': 'permissionCategoryName', 'type': 'str'},
        'is_licensed': {'key': 'isLicensed', 'type': 'bool'},
    }

    def __init__(self, view=None, create=None, edit=None, delete=None, permission_id=None, permission_code=None, permission_name=None, description=None, permission_category_name=None, is_licensed=None):
        super(BuildingsAndOrganizations, self).__init__()
        self.view = view
        self.create = create
        self.edit = edit
        self.delete = delete
        self.permission_id = permission_id
        self.permission_code = permission_code
        self.permission_name = permission_name
        self.description = description
        self.permission_category_name = permission_category_name
        self.is_licensed = is_licensed
