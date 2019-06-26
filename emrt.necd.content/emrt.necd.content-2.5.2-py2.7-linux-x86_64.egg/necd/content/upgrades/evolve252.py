import logging

import plone.api as api

logger = logging.getLogger(__name__)


def run(_):
    catalog = api.portal.get_tool('portal_catalog')
    rfs = [b.getObject() for b in catalog(portal_type='ReviewFolder')]

    for rf in rfs:
        if rf.type == 'projection':
            for obs in rf.objectValues():
                logger.info('Migrating %s', obs.absolute_url(1))
                obs.reindexObject()

    logger.info('Done!')
