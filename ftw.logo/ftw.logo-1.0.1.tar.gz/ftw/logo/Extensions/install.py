from ftw.logo.manual_override import BLOB_CACHEKEY
from ftw.logo.manual_override import ICON_OVERRIDES_KEY
from ftw.logo.manual_override import LOGO_OVERRIDES_KEY
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from zope.annotation.interfaces import IAnnotations


def uninstall(self):
    clean_up_content_annotations(self)

    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-ftw.logo:uninstall',
        ignore_dependencies=True)


def clean_up_content_annotations(portal):
    """
    Remove objects from content annotations in Plone site,

    This is mostly to remove objects which might make the site un-exportable
    when eggs / Python code have been removed.
    """
    output = StringIO()

    portal_catalog = getToolByName(portal, 'portal_catalog')
    brains = portal_catalog(object_provides='ftw.logo.manual_override.IManualOverrides')

    for b in brains:
        override_obj = b.getObject()
        annotations = IAnnotations(override_obj)
        for key in (ICON_OVERRIDES_KEY, LOGO_OVERRIDES_KEY, BLOB_CACHEKEY):
            if key in annotations:
                del annotations[key]
                print >> output, "Cleaned up annotation {} on {}".format(key, b.getPath())

    return output
