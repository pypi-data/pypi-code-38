from ftw.logo.interfaces import IIconConfig
from ftw.logo.interfaces import ILogo
from ftw.logo.interfaces import ILogoConfig
from ftw.logo.manual_override import BLOB_CACHEKEY
from ftw.logo.manual_override import OVERRIDES_FIXED_ID
from hashlib import sha256
from plone.app.caching.interfaces import IETagValue
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(ILogo)
@adapter(INavigationRoot, Interface)
class Logo(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_config(self, config_type):
        return getMultiAdapter((self.context, self.request), config_type)

    def get_logo_config(self):
        return getMultiAdapter((self.context, self.request), ILogoConfig)

    def get_icon_config(self):
        return getMultiAdapter((self.context, self.request), IIconConfig)


@implementer(IETagValue)
@adapter(Interface, Interface)
class LogoViewletETagValue(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cachekey = sha256()
        cachekey.update(getMultiAdapter(
                (self.context, self.request), ILogo).get_logo_config().cachekey)
        cachekey.update(getMultiAdapter(
                (self.context, self.request), ILogo).get_icon_config().cachekey)

        # self.context is a navigation root
        overridesItem = self.context.get(OVERRIDES_FIXED_ID)
        if overridesItem is not None:
            annotations = IAnnotations(overridesItem)
            blob_cachekey = annotations.get(BLOB_CACHEKEY, '')
        else:
            blob_cachekey = ''
        cachekey.update(blob_cachekey)
        return cachekey.hexdigest()
