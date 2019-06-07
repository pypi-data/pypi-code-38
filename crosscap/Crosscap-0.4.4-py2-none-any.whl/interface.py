"""
crosscap implementable interfaces
"""
from zope.interface import Interface, Attribute

class ICurrentUser(Interface):
    """
    A user with roles or capabilities that can be checked before granting resource access
    """
    def authenticate():
        """
        Confirm the user's identity using the available security factors

        @returns a truthy user object, or None
        """

    token = Attribute("cryptographic token associated with a request")

    roles = Attribute("a list of roles read from the current, authenticated user")

    def forbidden():
        """
        Do whatever is supposed to happen when a request is forbidden.

        The result of calling forbidden will be returned by the request call; e.g. in klein this may be a werkzeug.exceptions.Forbidden() object
        """

    def authenticated(user):
        """
        Handle the successfully-authenticated user (for example, by setting it as a property on the request handler)
        """
