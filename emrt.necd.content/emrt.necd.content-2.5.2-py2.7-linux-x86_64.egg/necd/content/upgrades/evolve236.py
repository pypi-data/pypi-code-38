from logging import getLogger

from Products.CMFCore.utils import getToolByName

import plone.api as api

from emrt.necd.content.upgrades import portal_workflow as upw
from emrt.necd.content.browser.carryover import clear_and_grant_roles


LOG = getLogger(__name__)


def fix_comment_permissions(context, catalog):
    wft = getToolByName(context, 'portal_workflow')
    type_mapping = upw.get_workflow_type_mapping(wft)

    queries = [
        dict(
            portal_type='Comment',
            review_state='initial',
            reindex_self_only=True,
        ),
    ]

    upw.upgrade(wft, catalog, type_mapping, queries)


def fix_carryover_local_roles(folder):
    for obs in folder.objectValues():
        if hasattr(obs, 'carryover_from') and obs.get_status() == 'pending':
            LOG.info('Fixing carryover for %s', obs.absolute_url(1))
            clear_and_grant_roles(obs)


def run(context):
    catalog = getToolByName(context, 'portal_catalog')
    portal = api.portal.get()

    fix_comment_permissions(context, catalog)
    fix_carryover_local_roles(portal['2019'])
