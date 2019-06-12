import plone.api as api
from Products.CMFCore.utils import getToolByName

def delete_voc(portal):
    atvm = getToolByName(portal, 'portal_vocabularies')
    atvm._delObject('parameter')

def reindex_objs(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    brains = catalog(portal_type='Observation')
    for brain in brains:
        brain.getObject().reindexObject(
            idxs=["NFR_Code_Inventory", "reference_year"]
        )

def run(_):
    portal = api.portal.get()

    delete_voc(portal)

    reindex_objs(portal)

