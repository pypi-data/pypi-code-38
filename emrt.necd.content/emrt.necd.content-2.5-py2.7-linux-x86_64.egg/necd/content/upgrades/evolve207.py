from functools import partial
from operator import attrgetter
import plone.api as api
from emrt.necd.content import utils
from emrt.necd.content import constants


COUNTRY = attrgetter('country')

APPEND_MINUS = partial(utils.append_string, '-')
COUNTRY_MSE = partial(APPEND_MINUS, constants.LDAP_MSEXPERT)


def set_role(rolename, principal):
    return (principal, (rolename, ))


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    review_folders = [
        brain.getObject() for brain in
        catalog(portal_type='ReviewFolder')
    ]

    for folder in review_folders:
        update_localroles(folder)
        folder.reindexObject()


def update_localroles(context):
    """ Set local roles for reviewfolder.
        The MSE-country LDAP groups don't have anything assigned
        so this time we can be greedy and not check existing roles.
    """
    observations = context.objectValues()

    # get existing observation countries
    countries = tuple(set(map(COUNTRY, observations)))

    # generate role string from country list
    roles_to_map = tuple(map(COUNTRY_MSE, countries))

    # generate (principal, (roles, )) tuple ready for usage
    set_mse_role = partial(set_role, constants.ROLE_MSE)
    local_roles = tuple(map(set_mse_role, roles_to_map))

    for principal, roles in local_roles:
        context.manage_setLocalRoles(principal, roles)
