from logging import getLogger
from plone import api


LOGGER = getLogger(__name__)


def run(_):
    upgrade_reviewfolders()

def upgrade_reviewfolders():
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type='ReviewFolder')

    for brain in brains:
        brain.getObject().type = 'inventory'