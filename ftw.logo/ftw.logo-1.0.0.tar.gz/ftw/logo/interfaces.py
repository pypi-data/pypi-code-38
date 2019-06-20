from zope.interface import Interface


class IFtwLogo(Interface):
    """ftw.logo Browser Layer
    """


class ILogo(Interface):
    """ Public interface for getting logo scales
    """

    def __init__(context, request):
        """Adapts context and request"""

    def get_config(config_type):
        """Get config based on config_type"""


class IIconConfig(Interface):
    """Adapter interface for logo customization adapter.
    """

    def __init__():
        """Adapts the zope application.
        """


class ILogoConfig(Interface):
    """Adapter interface for logo customization adapter.
    """

    def __init__():
        """Adapts the zope application.
        """
