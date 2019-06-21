from ftw.logo.converter import SCALES
from ftw.logo.converter import flatten_scales
from ftw.logo.interfaces import IIconConfig
from ftw.logo.interfaces import ILogo
from ftw.logo.interfaces import ILogoConfig
from ftw.logo.manual_override import OVERRIDES_FIXED_ID
from ftw.logo.manual_override import OVERRIDES_KEY_PATTERN
from ftw.logo.StringIOStreamIterator import StringIOStreamIterator
from plone.app.layout.globals.interfaces import IViewView
from plone.namedfile.browser import DisplayFile
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import mimetypes


CONFIGS = {
    'logo': ILogoConfig,
    'icon': IIconConfig,
}


@implementer(IPublishTraverse, IViewView)
class LogoView(BrowserView):

    def __init__(self, context, request):
        super(LogoView, self).__init__(context, request)
        self.scale = None
        self.config = None
        self.zcml_only = None

    def publishTraverse(self, request, name):
        if self.zcml_only is None and self.config is None and name == 'z':
            self.zcml_only = True
            return self
        elif self.config is None and name in CONFIGS:
            self.config_name = name
            self.config = CONFIGS[name]
            return self
        elif self.config and name in flatten_scales(SCALES):
            self.scale = name
            return self
        elif self.config and name == 'get_logo':
            self.scale = name
            return self
        else:
            raise NotFound()

    def __call__(self):
        if not self.config or not self.scale:
            raise BadRequest()

        if self.scale == 'get_logo':
            return self.handle_get_logo()

        check_overrides = not self.zcml_only
        return ((check_overrides and self.get_dx_overridden_image()) or
                self.get_zcml_configured_image())

    def get_dx_overridden_image(self):
        overridesItem = self.context.get(OVERRIDES_FIXED_ID)
        if overridesItem is None:
            return None
        # check if requested scale has been overridden and return it
        field_name = '{}_{}'.format(self.config_name, self.scale)
        field = getattr(overridesItem, field_name)
        if not field:
            # check if base logo/icon  has been overridden, then return the transformed BASE logo/icon
            base_field_name = '{}_BASE'.format(self.config_name)
            if getattr(overridesItem, base_field_name):
                annotations = IAnnotations(overridesItem)
                config = annotations.get(OVERRIDES_KEY_PATTERN.format(self.config_name), None)
                if config:
                    return self.show_config_scale(config)
        if not field:
            return None

        display_file = DisplayFile(overridesItem, self.request).publishTraverse(self.request, field_name or base_field_name)
        return display_file()

    def get_zcml_configured_image(self):
        config = getMultiAdapter(
            (self.context, self.request), ILogo).get_config(self.config)
        return self.show_config_scale(config)

    def show_config_scale(self, config):
        scale = config.get_scale(self.scale)
        response = self.request.response
        iterator = StringIOStreamIterator(scale['data'])
        extension = scale.get('extension') or scale['format'].lower()
        contenttype = mimetypes.types_map.get('.{}'.format(extension),
                                              'application/octet-stream')
        response.setHeader('X-Theme-Disabled', 'True')
        charset = '' if contenttype == 'application/octet-stream' else 'charset=utf-8'
        response.setHeader(
            'Content-Type', '{}; {}'.format(contenttype, charset))
        response.setHeader('Content-Length', iterator.len)
        if self.request.get('r'):
            # Do not set cache headers when no cachekey provided.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            response.setHeader('Cache-Control', 'public, max-age=31536000')
        return iterator

    def handle_get_logo(self):
        if self.has_dx_logo() and not self.has_dx_base():
            self.scale = 'LOGO'
            return self.get_dx_overridden_image()
        elif self.has_dx_base():
            self.scale = 'BASE'
            return self.get_dx_overridden_image()
        else:
            self.scale = 'BASE'

            config = getMultiAdapter(
                (self.context, self.request), ILogo).get_config(self.config)
            if config.primary_logo_scale:
                self.scale = config.primary_logo_scale.upper()

            return self.get_zcml_configured_image()

    def has_dx_logo(self):
        overridesItem = self.context.get(OVERRIDES_FIXED_ID)
        if not overridesItem:
            return False
        return bool(overridesItem.logo_LOGO)

    def has_dx_base(self):
        overridesItem = self.context.get(OVERRIDES_FIXED_ID)
        if not overridesItem:
            return False
        return bool(overridesItem.logo_BASE)
