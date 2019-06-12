from logging import getLogger

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
import plone.api as api


def run(_):
    logger = getLogger(__name__)
    add_vocabulary_terms(logger)
    reindex_observations(logger)


def add_vocabulary_terms(logger):
    vt = api.portal.get_tool('portal_vocabularies')
    vocab = vt.get('parameter')
    new = (
        ('fus', 'Fuel used/sold'),
        ('gc', 'Geographical coverage'),
    )

    for key, val in new:
        if key not in vocab.keys():
            vocab.addTerm(key, val)
            logger.info('Added term: %s.', (key, val))
        else:
            logger.info('Term: %s already exists.', (key, val))


def reindex_observations(logger):
    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(portal_type='Observation')
    brains_len = len(brains)
    logger.info('Found %s brains.', brains_len)
    observations = (brain.getObject() for brain in brains)
    for idx, observation in enumerate(observations, start=1):
        catalog.catalog_object(observation, idxs=tuple(), update_metadata=1)
        if idx % 50 == 0:
            logger.info('Done %s/%s.', idx, brains_len)
