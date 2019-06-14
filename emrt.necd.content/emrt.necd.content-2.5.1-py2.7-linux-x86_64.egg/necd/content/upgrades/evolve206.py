from functools import partial
from operator import itemgetter
import plone.api as api
from emrt.necd.content.constants import ROLE_SE


PRINCIPAL = itemgetter(0)
ROLES = itemgetter(1)


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    review_folders = [brain.getObject() for brain in catalog(portal_type='ReviewFolder')]
    for folder in review_folders:
        update_localroles(folder)
        folder.reindexObject()


def update_localroles(context):
    """ Recursively update local roles """
    map(update_localroles, context.objectValues())
    new_roles = map(updated_roles, context.get_local_roles())
    for principal, roles in new_roles:
        context.manage_setLocalRoles(principal, roles)


def updated_roles(entry):
    """ Rename 'NECDReviewer' to ROLE_SE """
    def rename(src, dest, item):
        return dest if item == src else item

    necdrev_to_se = partial(rename, 'NECDReviewer', ROLE_SE)

    new_roles = tuple(set(map(necdrev_to_se, ROLES(entry))))
    return (PRINCIPAL(entry), new_roles)
