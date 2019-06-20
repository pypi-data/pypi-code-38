from ftw.logo.converter import convert
from ftw.logo.converter import make_transformer
from ftw.logo.converter import SCALES
from ftw.logo.image import Image
from ftw.logo.interfaces import IIconConfig
from ftw.logo.interfaces import ILogoConfig
from hashlib import sha256
from textwrap import wrap
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements


def get_cachekey_from_blob(*args):
    cachekey = sha256()
    for blob in args:
        if blob:
            for chunk in wrap(blob, 4096):
                cachekey.update(chunk)
    return cachekey.hexdigest()


class AbstractConfig(object):

    base = None
    logo = None
    mobile = None
    favicon = None
    primary_logo_scale = None

    def __init__(self, **kwargs):
        if 'base' not in kwargs:
            raise ConfigurationError('A base svg is required')

        self.base = Image(filename=kwargs['base'])

        if 'logo' in kwargs:
            self.logo = Image(filename=kwargs['logo'])
        if 'mobile' in kwargs:
            self.mobile = Image(filename=kwargs['mobile'])
        if 'favicon' in kwargs:
            self.favicon = Image(filename=kwargs['favicon'])

        if 'height' in kwargs:
            # Update by reference the transformer with the new height
            SCALES['LOGOS']['LOGO'] = make_transformer(height=kwargs['height'])
        if 'mobile_height' in kwargs:
            # Update by reference the transformer with the new height
            SCALES['LOGOS']['MOBILE_LOGO'] = make_transformer(height=kwargs['mobile_height'])

        self.cachekey = get_cachekey_from_blob(
            self.base.make_blob(),
            self.logo and self.logo.make_blob() or None,
            self.mobile and self.mobile.make_blob() or None,
            self.favicon and self.favicon.make_blob() or None,)
        self.scales = {}
        self.collect_scales()
        self.set_primary_logo_scale(**kwargs)

    def add_scale(self, name, scale):
        self.scales[name] = scale

    def collect_scales(self):
        raise NotImplemented()  # pragma: no cover

    def get_scale(self, name):
        return self.scales[name]

    def set_primary_logo_scale(self, **kwargs):
        if 'primary_logo_scale' in kwargs:
            self.primary_logo_scale = kwargs['primary_logo_scale']


class LogoConfig(AbstractConfig):
    """Logo config entry.
    """

    implements(ILogoConfig)

    def collect_scales(self):
        for scale in SCALES['LOGOS']:
            if getattr(self, scale.lower(), None):
                self.add_scale(scale, convert(getattr(self, scale.lower()), scale))
            else:
                self.add_scale(scale, convert(self.base, scale))


class IconConfig(AbstractConfig):
    """Icon config entry.
    """

    implements(IIconConfig)

    def collect_scales(self):
        for scale in SCALES['ICONS']:
            if getattr(self, scale.lower(), None):
                self.add_scale(scale, convert(getattr(self, scale.lower()), scale))
            else:
                self.add_scale(scale, convert(self.base, scale))


class AbstractConfigOverride(AbstractConfig):

    def __init__(self, blobImage):
        base_img = Image(blob=blobImage.data, format='svg')
        self.cachekey = get_cachekey_from_blob(blobImage.data)
        self.scales = {}
        self.collect_scales(base_img)


class LogoConfigOverride(AbstractConfigOverride):
    """Logo config (TTW) overrides.
    """

    implements(ILogoConfig)

    def collect_scales(self, base_img):
        for scale in SCALES['LOGOS']:
            self.add_scale(scale, convert(base_img, scale))


class IconConfigOverride(AbstractConfigOverride):
    """Icon config (TTW) overrides.
    """

    implements(IIconConfig)

    def collect_scales(self, base_img):
        for scale in SCALES['ICONS']:
            self.add_scale(scale, convert(base_img, scale))
