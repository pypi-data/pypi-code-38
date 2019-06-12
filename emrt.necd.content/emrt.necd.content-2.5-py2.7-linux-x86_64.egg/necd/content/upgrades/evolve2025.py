from functools import partial
from operator import itemgetter
from logging import getLogger

import plone.api as api

from emrt.necd.content.constants import LDAP_BASE
from emrt.necd.content.constants import ROLE_LR
from emrt.necd.content.constants import ROLE_SE
from emrt.necd.content.constants import ROLE_MSA

LOGGER = getLogger(__name__)


REVOKE_ROLES = (ROLE_LR, ROLE_SE, ROLE_MSA)


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
        if set(REVOKE_ROLES).intersection(roles(item))
    )

    users = tuple(
        name for name in principals
        if not name.startswith(LDAP_BASE)
    )

    revoker = partial(
        api.user.revoke_roles,
        roles=REVOKE_ROLES,
        obj=obj
    )

    if users:
        map(revoker, users)
        obj.reindexObjectSecurity()

        LOGGER.info(
            'Revoked %s from %s on %s',
            REVOKE_ROLES,
            users,
            obj.absolute_url(1)
        )

    # new brain metadata is added by catalog.xml
    # observation_sent_to_msc and observation_sent_to_mse
    obj.reindexObject()


def get_objects(catalog, portal_type):
    brains = catalog(portal_type=portal_type)
    return tuple(brain.getObject() for brain in brains)
