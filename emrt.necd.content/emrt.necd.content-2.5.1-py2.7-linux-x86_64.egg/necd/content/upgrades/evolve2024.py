from functools import partial
from operator import itemgetter
from logging import getLogger

import plone.api as api

from emrt.necd.content.constants import LDAP_MSEXPERT
from emrt.necd.content.constants import ROLE_MSE

LOGGER = getLogger(__name__)


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    objects = get_objects(catalog, ('ReviewFolder', 'Observation'))

    obj_len = len(objects)
    LOGGER.info('Found %s objects.', obj_len)

    for idx, obj in enumerate(objects, start=1):
        do_upgrade(obj)
        if idx % 50 == 0:
            LOGGER.info('Done %s/%s.', idx, obj_len)


def do_upgrade(obj):
    principal = itemgetter(0)
    roles = itemgetter(1)

    local_roles = obj.get_local_roles()

    principals = tuple(
        principal(item) for item in local_roles
        if ROLE_MSE in roles(item)
    )

    groups = tuple(
        name for name in principals
        if name.startswith(LDAP_MSEXPERT)
    )

    revoker = partial(
        api.group.revoke_roles,
        roles=(ROLE_MSE, ),
        obj=obj
    )

    map(revoker, groups)

    obj.reindexObjectSecurity()

    LOGGER.info('Revoked %s from %s', ROLE_MSE, groups)


def get_objects(catalog, portal_type):
    brains = catalog(portal_type=portal_type)
    return tuple(brain.getObject() for brain in brains)

