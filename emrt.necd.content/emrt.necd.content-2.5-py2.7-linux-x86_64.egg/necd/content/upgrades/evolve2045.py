import logging
import plone.api as api

from emrt.necd.content.observation import set_title_to_observation

logger = logging.getLogger(__name__)


def gen_get_observations(tool):
    brains = tool(portal_type='Observation')
    len_brains = len(brains)
    logger.info('Found %s brains.', len_brains)
    for idx, brain in enumerate(brains, start=1):
        yield brain.getObject()
        logger.info('Updating %s/%s.', idx, len_brains)


def run(_):
    tool = api.portal.get_tool('portal_catalog')
    for obs in gen_get_observations(tool):
        # remove local roles from "sector" principals
        _current_roles = obs.get_local_roles()
        _principals = [p for p, _ in _current_roles if 'sector' in p]
        obs.manage_delLocalRoles(_principals)

        # update title and roles
        set_title_to_observation(obs, None)
