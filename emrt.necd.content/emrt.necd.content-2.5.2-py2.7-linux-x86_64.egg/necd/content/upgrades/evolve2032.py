from logging import getLogger

from Products.CMFCore.utils import getToolByName
import plone.api as api
from emrt.necd.content.constants import ROLE_MSE


def run(_):
    logger = getLogger(__name__)
    catalog = api.portal.get_tool('portal_catalog')

    query = dict(portal_type='Observation', observation_sent_to_mse=True)
    brains = catalog(**query)
    brains_len = len(brains)
    logger.info('Found %s brains.', brains_len)
    for idx, brain in enumerate(brains, start=1):
        obj = brain.getObject()
        test_user = 'necd_eea_{}_exp'.format(obj.country)
        api.user.grant_roles(username=test_user, roles=[ROLE_MSE], obj=obj)
        obj.reindexObjectSecurity()
        if idx % 50 == 0:
            logger.info('Done %s/%s.', idx, brains_len)
