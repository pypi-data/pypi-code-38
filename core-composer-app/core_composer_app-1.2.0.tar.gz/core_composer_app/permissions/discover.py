""" Initialize permissions for core composer app
"""
from django.contrib.auth.models import Permission, Group
from core_main_app.permissions import rights as main_rights
from core_composer_app.permissions import rights as composer_rights


def init_permissions():
    """Initialization of groups and permissions.

    Returns:

    """
    try:
        # Get or Create the default group
        default_group, created = Group.objects.get_or_create(name=main_rights.default_group)

        # Get composer permissions
        composer_access_perm = Permission.objects.get(codename=composer_rights.composer_access)
        composer_save_template_perm = Permission.objects.get(codename=composer_rights.composer_save_template)
        composer_save_type_perm = Permission.objects.get(codename=composer_rights.composer_save_type)

        # add permissions to default group
        default_group.permissions.add(composer_access_perm,
                                      composer_save_template_perm,
                                      composer_save_type_perm)
    except Exception, e:
        print('ERROR : Impossible to init the rules : ' + e.message)
