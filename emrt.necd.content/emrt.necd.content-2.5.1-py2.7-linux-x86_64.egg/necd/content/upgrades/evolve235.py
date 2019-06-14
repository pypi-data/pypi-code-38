from logging import getLogger

import plone.api as api
from Products.CMFCore.utils import getToolByName


LOGGER = getLogger(__name__)


HIGHLIGHT = {
    '2017-rec': 'rec-fu',
    '2017-re': 're-fu',
    '2017-tc': 'tc-fu',
}


def delete_voc(portal):
    atvm = getToolByName(portal, 'portal_vocabularies')
    atvm._delObject('pollutants')
    atvm._delObject('highlight_projection')
    atvm._delObject('highlight')


def migrate_obs_highlight(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    query = dict(
        portal_type='Observation',
        highlight=dict(
            query=HIGHLIGHT.keys(),
            operator='or'
        )
    )

    brains = catalog(**query)
    len_brains = len(brains)

    for idx, brain in enumerate(brains, start=1):
        obj = brain.getObject()
        obj.highlight = [HIGHLIGHT.get(t, t) for t in obj.highlight]
        LOGGER.info(
            '[%s/%s] Updating %s',
            idx, len_brains, obj.absolute_url(1)
        )
        catalog.catalog_object(
            obj,
            idxs=(
                'highlight',
            ),
            update_metadata=1
        )


def run(_):
    portal = api.portal.get()
    delete_voc(portal)
    migrate_obs_highlight(portal)
