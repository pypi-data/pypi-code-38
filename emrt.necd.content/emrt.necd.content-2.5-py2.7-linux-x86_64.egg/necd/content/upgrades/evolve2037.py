from functools import partial
from logging import getLogger

import plone.api as api


LOGGER = getLogger(__name__)


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    wft = api.portal.get_tool('portal_workflow')

    query_catalog = partial(get_objects, catalog)

    upgrade_conclusions = partial(
        upgrade_objects,
        wft=wft,
        permissions=('Delete portal content', ),
    )

    upgrade_observations = partial(
        upgrade_objects,
        wft=wft,
        permissions=('emrt.necd.content: View Conclusion Discussion', )
    )

    upgrade_conclusions(query_catalog('Conclusions'))
    upgrade_observations(query_catalog('Observation'))


def upgrade_objects(objects, wft, permissions):
    obj_len = len(objects)
    LOGGER.info('Found %s objects.', obj_len)

    if not objects:
        return

    workflows = wft.getWorkflowsFor(objects[0].portal_type)
    wf = workflows[0]

    for idx, obj in enumerate(objects, start=1):
        do_upgrade(wft, wf, obj, permissions)
        if idx % 50 == 0:
            LOGGER.info('Done %s/%s.', idx, obj_len)


def do_upgrade(wft, wf, obj, permissions):
    obj_state = wft.getInfoFor(obj, name='review_state')
    state = wf.states.get(obj_state)

    for perm in permissions:
        roles = state.getPermissionInfo(perm)
        obj.manage_permission(
            perm,
            roles=roles['roles'],
            acquire=roles['acquired']
        )

    LOGGER.info('Updated permissions on %s', obj.absolute_url())


def get_objects(catalog, portal_type):
    brains = catalog(portal_type=portal_type)
    return tuple(brain.getObject() for brain in brains)
