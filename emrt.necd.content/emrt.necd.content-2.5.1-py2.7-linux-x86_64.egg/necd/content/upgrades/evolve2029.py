from logging import getLogger

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
import plone.api as api


NFR_CODES = ('1A2gvii ', '2H3 ')

def run(_):
    logger = getLogger(__name__)
    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(portal_type='Observation', nfr_code=NFR_CODES)
    brains_len = len(brains)
    logger.info('Found %s brains.', brains_len)
    observations = (brain.getObject() for brain in brains)
    for idx, observation in enumerate(observations, start=1):
        observation.nfr_code = observation.nfr_code.strip()
        observation.reindexObject()
        if idx % 50 == 0:
            logger.info('Done %s/%s.', idx, brains_len)
