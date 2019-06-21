from ftw.logo import _
from ftw.logo.logoconfig import get_cachekey_from_blob
from ftw.logo.logoconfig import IconConfigOverride
from ftw.logo.logoconfig import LogoConfigOverride
from hashlib import sha256
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.browser import edit
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.namedfile.field import INamedBlobImage
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import Invalid
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema import getFieldsInOrder
import transaction


OVERRIDES_FIXED_ID = 'ftw-logo-overrides'
# Annotations keys
LOGO_OVERRIDES_KEY = 'ftw.logo.logo_overrides'
ICON_OVERRIDES_KEY = 'ftw.logo.icon_overrides'
BLOB_CACHEKEY = 'ftw.logo.blob_cachekey'
OVERRIDES_KEY_PATTERN = 'ftw.logo.{}_overrides'


def svg_file_only(value):
    if value.contentType != 'image/svg+xml':
        raise Invalid(
            u"This image must be a SVG file " +
            u"({} supplied)".format(value.contentType)
        )
    return True


def png_file_only(value):
    if value.contentType != 'image/png':
        raise Invalid(
            u"This image must be a PNG file " +
            u"({} supplied)".format(value.contentType)
        )
    return True


class IManualOverrides(model.Schema):

    # Note: The field names are carefully constructed as one of:
    #   logo_<logo scale name>, or
    #   icon_<icon scale name>
    # The form (manual_override.pt) depends on this to find the ZCML
    # default image

    logo_BASE = NamedBlobImage(
        title=_(u"SVG base logo"),
        description=_(u"Overriding the base logo will generate an override "
                      u"for BOTH logos below if not already set."),
        required=False,
        constraint=svg_file_only,
    )

    logo_LOGO = NamedBlobImage(
        title=_(u"Standard (desktop) logo (PNG)"),
        required=False,
        constraint=png_file_only,
    )

    logo_MOBILE_LOGO = NamedBlobImage(
        title=_(u"Mobile logo (PNG)"),
        required=False,
        constraint=png_file_only,
    )

    icon_BASE = NamedBlobImage(
        title=_(u"SVG base icon"),
        description=_(u"Overriding the base icon will generate an "
                      u"override for ALL icons below if not already set."),
        required=False,
        constraint=svg_file_only,
    )

    icon_APPLE_TOUCH_ICON = NamedBlobImage(
        title=_(u"Apple touch icon"),
        required=False,
        constraint=png_file_only,
    )

    icon_FAVICON_32X32 = NamedBlobImage(
        title=_(u"Favicon 32x32"),
        required=False,
        constraint=png_file_only,
    )

    icon_FAVICON_16X16 = NamedBlobImage(
        title=_(u"Favicon 16x16"),
        required=False,
        constraint=png_file_only,
    )

    icon_MSTILE_150X150 = NamedBlobImage(
        title=_(u"Mstile icon 150x150"),
        required=False,
        constraint=png_file_only,
    )

    icon_ANDROID_192X192 = NamedBlobImage(
        title=_(u"Android icon 192x192"),
        required=False,
        constraint=png_file_only,
    )

    icon_ANDROID_512X512 = NamedBlobImage(
        title=_(u"Android icon 512x512"),
        required=False,
        constraint=png_file_only,
    )

    icon_FAVICON = NamedBlobImage(
        title=_(u"Favicon"),
        required=False,
        constraint=png_file_only,
    )


@adapter(IManualOverrides, IObjectModifiedEvent)
def overrides_changed(override_object, event):
    annotations = IAnnotations(override_object)
    if override_object.logo_BASE:
        annotations[LOGO_OVERRIDES_KEY] = LogoConfigOverride(override_object.logo_BASE)
    if override_object.icon_BASE:
        annotations[ICON_OVERRIDES_KEY] = IconConfigOverride(override_object.icon_BASE)

    # calculate a cachekey combining all blob fields in this object
    cachekey = sha256()
    for schemata in iterSchemata(override_object):
        for name, field in getFieldsInOrder(schemata):
            try:
                value = field.get(schemata(override_object))
                if value is not field.missing_value and field.schema == INamedBlobImage:
                    blobdata = field.get(override_object).data
                    cachekey.update("|{}".format(get_cachekey_from_blob(blobdata)))
                    continue
            except AttributeError:
                pass
            cachekey.update("|")
    annotations[BLOB_CACHEKEY] = cachekey.hexdigest()


class CreateOverridesIfReqdForm(BrowserView):
    """
    Create IManualOverrides if it does not exist and redirect to it's edit form
    """
    def __call__(self):
        navroot = self.context
        overridesItem = navroot.get(OVERRIDES_FIXED_ID)
        if overridesItem is None:

            overridesItem = createContentInContainer(
                navroot,
                'ftw.logo.ManualOverrides',
                checkConstraints=False,
                id=OVERRIDES_FIXED_ID,
                title='Logo and Icon Overrides',
                description='Manual overrides for the site logo(s) and icons',
            )
            transaction.get().commit()

            self.request.response.redirect('{}/@@edit'.format(
                overridesItem.absolute_url_path()
            ))
            return
        self.request.response.redirect('{}/view'.format(
            overridesItem.absolute_url_path()
        ))
        return


class ManualOverrideMixin(object):
    def get_origin_for_scale(self, fullscalename):
        """ Lookup HTML class for depending on authoritative origin for a particular scale """
        fieldname = fullscalename.replace('/', '_')
        config_name = fullscalename.split('/')[0]
        if getattr(self.context, fieldname):
            return 'direct_override'
        if getattr(self.context, '{}_BASE'.format(config_name)):
            return 'scaled_base_override'
        else:
            return 'zcml'


class EditManualOverrideForm(edit.DefaultEditForm, ManualOverrideMixin):
    label = _(u"Edit Manual Logo and Icon Overrides")
    description = _(u"Site logos and icons set in ZCML are shown in " +
                    u"the left column. Overrides from this form are " +
                    u"shown in the right column")

    template = ViewPageTemplateFile('manual_override.pt')

    def get_origin_for_scale(self, fullscalename):
        """ Lookup HTML class for depending on authoritative origin for a particular scale """
        fieldname = fullscalename.replace('/', '_')
        config_name = fullscalename.split('/')[0]
        if getattr(self.context, fieldname):
            return 'direct_override'
        if getattr(self.context, '{}_BASE'.format(config_name)):
            return 'scaled_base_override'
        else:
            return 'zcml'


class ManualOverrideView(DefaultView, ManualOverrideMixin):
    pass
