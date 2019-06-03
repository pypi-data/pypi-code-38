""" Discover rules for core explore keyword app
"""
from core_explore_keyword_app.permissions import rights as explore_keyword_rights
from core_main_app.permissions import rights as main_rights


def init_permissions(apps):
    """Initialization of groups and permissions

    Returns:

    """
    try:
        group = apps.get_model("auth", "Group")
        permission = apps.get_model("auth", "Permission")

        # Get or Create the default group
        default_group, created = group.objects.get_or_create(name=main_rights.default_group)

        # Get explore keyword permissions
        explore_access_perm = permission.objects.get(codename=explore_keyword_rights.explore_keyword_access)

        # add permissions to default group
        default_group.permissions.add(explore_access_perm)
    except Exception, e:
        print('ERROR : Impossible to init the permissions for core_explore_keyword_app : ' + e.message)
