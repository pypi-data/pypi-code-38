from zope.configuration.exceptions import ConfigurationError
import gocept.pagelet.viewletpage
import z3c.pagelet.browser
import z3c.pagelet.interfaces
import z3c.pagelet.zcml
import z3c.template.zcml
import zope.browsermenu.field
import zope.browserpage.metaconfigure
import zope.configuration.fields
import zope.interface
import zope.publisher.interfaces.browser
import zope.viewlet.metaconfigure


class IPageletDirective(z3c.pagelet.zcml.IPageletDirective):
    """A directive to easily register a new pagelet with a layout template."""

    for_ = zope.configuration.fields.Tokens(
        title=u"Specifications of the objects to be viewed",
        description=u"""This should be a list of interfaces or classes""",
        required=True,
        value_type=zope.configuration.fields.GlobalObject(
              missing_value=object(),
        ),
    )

    class_ = zope.configuration.fields.GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the pagelet.",
        required=False,
    )

    template = zope.configuration.fields.Path(
        title=u'Layout template.',
        description=u"Refers to a file containing a page template (should "
        "end in extension ``.pt`` or ``.html``).",
        required=False,
    )

    title = zope.configuration.fields.MessageID(
        title=u"The browser menu label for the page (view)",
        description=u"""
          This attribute must be supplied if a menu attribute is
          supplied.
          """,
        required=False
    )

    menu = zope.browsermenu.field.MenuField(
        title=u"The browser menu to include the page (view) in.",
        description=u"""
          Many views are included in menus. It's convenient to name
          the menu in the page directive, rather than having to give a
          separate menuItem directive.  'zmi_views' is the menu most often
          used in the Zope management interface.
          </description>
          """,
        required=False
    )


def pageletDirective(  # noqa
        _context, name, permission, class_=None, for_=zope.interface.Interface,
        layer=zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        allowed_interface=None, allowed_attributes=None, template=None,
        title=None, menu=None,
        **kwargs):
    """Register a new pagelet with a layout template."""
    if class_:
        new_class = class_
    else:
        class_name = 'SimplePagelet'
        if template:
            class_name += ' from %s' % str(template)
            new_class = type(class_name, (object, ), {})

    original_pageletDirective(
        _context, new_class, name, permission,
        for_=tuple(for_), layer=layer,
        allowed_interface=allowed_interface,
        allowed_attributes=allowed_attributes)

    if template:
        z3c.template.zcml.templateDirective(
            _context, template, for_=new_class, layer=layer)

    zope.browserpage.metaconfigure._handle_menu(
        _context, menu, title, tuple(for_), name, permission, layer)


class ViewletPageDirective(object):
    """Directive to register a new pagelet with a layout template."""

    def __init__(self, _context, name, permission,
                 class_=gocept.pagelet.viewletpage.ViewletPage,
                 **kwargs):
        self._context = _context
        self.name = name
        self.permission = permission
        self.class_ = class_
        self.kwargs = kwargs

    def __call__(self):
        z3c.pagelet.zcml.pageletDirective(
            self._context, self.class_, self.name, self.permission,
            **self.kwargs)

    def viewlet(self, _context, name, permission, layer=None, **kwargs):
        kwargs["manager"] = gocept.pagelet.viewletpage.IViewletPageManager
        zope.viewlet.metaconfigure.viewletDirective(
            _context, name, permission,
            layer=layer or self.kwargs.get("layer"),
            **kwargs)


def original_pageletDirective(  # noqa
        _context, class_, name, permission, for_=(zope.interface.Interface,),
        layer=zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        provides=z3c.pagelet.interfaces.IPagelet,
        allowed_interface=None, allowed_attributes=None, **kwargs):
    """The original pagelet directive."""
    # Security map dictionary
    required = {}

    # Get the permission; mainly to correctly handle CheckerPublic.
    permission = zope.browserpage.metaconfigure._handle_permission(
        _context, permission)

    # The class must be specified.
    if not class_:
        raise ConfigurationError("Must specify a class.")

    if not zope.interface.interfaces.IInterface.providedBy(provides):
        raise ConfigurationError("Provides interface provide IInterface.")

    ifaces = list(zope.interface.Declaration(provides).flattened())
    if z3c.pagelet.interfaces.IPagelet not in ifaces:
        raise ConfigurationError("Provides interface must inherit IPagelet.")

    # Build a new class that we can use different permission settings if we
    # use the class more then once.
    cdict = {}
    cdict['__name__'] = name
    cdict.update(kwargs)
    new_class = type(
        class_.__name__, (class_, z3c.pagelet.browser.BrowserPagelet), cdict)

    # Set up permission mapping for various accessible attributes
    zope.browserpage.metaconfigure._handle_allowed_interface(
        _context, allowed_interface, permission, required)
    zope.browserpage.metaconfigure._handle_allowed_attributes(
        _context, allowed_attributes, permission, required)
    zope.browserpage.metaconfigure._handle_allowed_attributes(
        _context, kwargs.keys(), permission, required)
    zope.browserpage.metaconfigure._handle_allowed_attributes(
        _context, ('__call__', 'browserDefault', 'update', 'render',
                   'publishTraverse'), permission, required)

    # Register the interfaces.
    for i in for_:
        zope.browserpage.metaconfigure._handle_for(_context, i)

    # provide the custom provides interface if not allready provided
    if not provides.implementedBy(new_class):
        zope.interface.classImplements(new_class, provides)

    # Create the security checker for the new class
    zope.security.checker.defineChecker(
        new_class, zope.security.checker.Checker(required))

    # register pagelet
    _context.action(
        discriminator=('pagelet',) + for_ + (layer, name),
        callable=zope.component.zcml.handler,
        args=('registerAdapter',
              new_class, for_ + (layer,), provides, name, _context.info),)
