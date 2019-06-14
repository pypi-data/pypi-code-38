from logging import getLogger

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
import plone.api as api


def run(_):
    logger = getLogger(__name__)
    catalog = api.portal.get_tool('portal_catalog')
    observations = get_observations(catalog)
    obs_len = len(observations)
    logger.info('Found %s observations.', obs_len)
    for idx, obs in enumerate(observations, start=1):
        do_upgrade(obs, catalog)
        if idx % 50 == 0:
            logger.info('Done %s/%s.', idx, obs_len)


def do_upgrade(obs, catalog):
    rename_ms_key_category(obs)
    reindex_observation(obs, catalog)


def rename_ms_key_category(obs):
    old_fname = 'ms_key_catagory'
    new_fname = 'ms_key_category'
    if hasattr(obs, old_fname):
        old_fvalue = getattr(obs, old_fname)
        setattr(obs, new_fname, old_fvalue)
        delattr(obs, old_fname)


def reindex_observation(obs, catalog):
    catalog.catalog_object(
        obs,
        idxs=tuple(['ms_key_category']),
        update_metadata=1
    )


def get_observations(catalog):
    brains = catalog(portal_type='Observation')
    return tuple(brain.getObject() for brain in brains)
