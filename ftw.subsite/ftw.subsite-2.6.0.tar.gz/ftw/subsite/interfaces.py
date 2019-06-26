from zope.interface import Interface
from plone.app.portlets.interfaces import IColumn


class ISubsite(Interface):
    """
    marker interface for subsite content type
    """


class ISubsiteColumn(IColumn):
    """
    Marker Inerface for front view columns
    """


class IFtwSubsiteLayer(Interface):
    """
    Browserlayer
    """

class ILanguages(Interface):
    """Adapter for handling language specific questions for a context.
    It respects interaction between a certain set of connected subsites
    with different translations as well as for subsites connected to the
    site root regarding languages.

    The adapter can be used on any context and finds the next parent subsite
    or plone site root which dictactes the settings for the contents below.
    """

    def __init__(context, request):
        """ILanguages is a multi adapter adapting context and request.
        """

    def get_current_language(self):
        """Returns the language active in this area as dict.
        Example:

        >>> {'url': 'http://url/to/language/root',
        ...  'title': 'English',
        ...  'code': 'en'}
        """

    def get_related_languages(self):
        """Returns a list of dicts of all related languages active in this
        area but not including itself.

        Example language dict:

        >>> {'url': 'http://url/to/language/root',
        ...  'title': 'English',
        ...  'code': 'en'}
        """
