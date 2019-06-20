from ftw.logo.interfaces import IIconConfig
from ftw.logo.interfaces import ILogoConfig
from ftw.logo.logoconfig import IconConfig
from ftw.logo.logoconfig import LogoConfig
from zope import schema
from zope.component.zcml import handler
from zope.configuration import fields
from zope.configuration.fields import GlobalInterface
from zope.interface import Interface


class ILogoDirective(Interface):

    for_ = GlobalInterface(
        title=u'The interface the context should provide.',
        required=False)

    layer = GlobalInterface(
        title=u'The interface the request should provide.',
        required=False)

    base = fields.Path(
        title=u'Relative path to the logo svg file.',
        required=True)

    logo = fields.Path(
        title=u'Relative path to the logo image file.',
        required=False)

    mobile = fields.Path(
        title=u'Relative path to the mobile logo image file.',
        required=False)

    primary_logo_scale = schema.Text(
        title=u'Relative path to the mobile logo image file.',
        required=False)

    height = schema.Text(
        title=u'Relative path to the mobile logo image file.',
        required=False)

    mobile_height = schema.Text(
        title=u'Relative path to the mobile logo image file.',
        required=False)


class IIconDirective(Interface):

    for_ = GlobalInterface(
        title=u'The interface the context should provide.',
        required=False)

    layer = GlobalInterface(
        title=u'The interface the request should provide.',
        required=False)

    base = fields.Path(
        title=u'Relative path to the icon file.',
        required=True)

    favicon = fields.Path(
        title=u'Relative path to the favicon file.',
        required=False)


def registerLogo(_context, **kwargs):
    component = LogoConfig(**kwargs)

    def adapter_factory(context, request):
        return component

    requires = (kwargs.get('for_', Interface),
                kwargs.get('layer', Interface))

    _context.action(
        discriminator=('logo:logo',) + requires,
        callable=handler,
        args=('registerAdapter', adapter_factory, requires, ILogoConfig, ''))


def registerIcon(_context, **kwargs):
    component = IconConfig(**kwargs)

    def adapter_factory(context, request):
        return component

    requires = (kwargs.get('for_', Interface),
                kwargs.get('layer', Interface))

    _context.action(
        discriminator=('logo:icon',) + requires,
        callable=handler,
        args=('registerAdapter', adapter_factory, requires, IIconConfig, ''))
