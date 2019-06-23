from twisted.cred import error
from twisted.python.components import registerAdapter, proxyForInterface
from twisted.web._auth.wrapper import UnauthorizedResource
from twisted.web.resource import IResource, ErrorPage
from twisted.web.server import Session
from twisted.web.util import DeferredResource
from zope.interface import Interface, Attribute, implements

from txhttputil import AuthUserDetails
from txhttputil import createRootResource
from .AuthResource import LoginResource, LoginSucceededResource

__author__ = 'synerty'


class IAuth(Interface):
  value = Attribute("An int value which counts up once per page view.")


class Auth(object):
  implements(IAuth)

  def __init__(self, session):
    self.userAccess = AuthUserDetails()
    self.userAccess.loggedIn = False
    self.userAccess.readOnly = True


registerAdapter(Auth, Session, IAuth)


class AuthSessionWrapper(object):
  implements(IResource)
  isLeaf = False


  def _authorizedResource(self, request):
    """
    Get the L{IResource} which the given request is authorized to receive.
    If the proper authorization headers are present, the resource will be
    requested from the portal.  If not, an anonymous login_page attempt will be
    made.
    """

    auth = IAuth(request.getSession())
    if auth.userAccess.loggedIn:
      request.getSession().touch()
      return createRootResource(auth.userAccess)

    # TRY Basic HTTP Authentication
    authheader = request.getHeader('authorization')
    if authheader:
      factory, respString = self._selectParseHeader(authheader)
      if factory is None:
        return LoginResource()
      try:
        credentials = factory.decode(respString, request)
      except error.LoginFailed:
        return LoginResource()
      except:
        print("Unexpected failure from credentials factory")
        return ErrorPage(500, None, None)
      else:
        return DeferredResource(self._login(credentials))


    # TRY form based authentication
    a = request.args
    if request.method == "POST":
      if ("username" in a
          and "password" in a
          and a['username'][0] == "test"
          and a["password"][0] == "test"):
        auth.userAccess.loggedIn = True
        auth.userAccess.readOnly = False
        request.redirect(request.path)
        return LoginSucceededResource()

    # Return login_page form
    return LoginResource()


  def render(self, request):
    """
    Find the L{IResource} avatar suitable for the given request, if
    possible, and render it.  Otherwise, perhaps render an error page
    requiring authorization or describing an internal server failure.
    """
    return self._authorizedResource(request).render(request)


  def getChildWithDefault(self, path, request):
    """
    Inspect the Authorization HTTP header, and return a deferred which,
    when fired after successful authentication, will return an authorized
    C{Avatar}. On authentication failure, an C{UnauthorizedResource} will
    be returned, essentially halting further dispatch on the wrapped
    resource and all children
    """
    # Don't consume any segments of the request - this class should be
    # transparent!
    request.postpath.insert(0, request.prepath.pop())
    return self._authorizedResource(request)


  def _login(self, credentials):
    """
    Get the L{IResource} avatar for the given credentials.

    @return: A L{Deferred} which will be called back with an L{IResource}
        avatar or which will errback if authentication fails.
    """
    d = self._portal.login(credentials, None, IResource)
    d.addCallbacks(self._loginSucceeded, self._loginFailed)
    return d


  def _loginSucceeded(self, xxx_todo_changeme):
    """
    Handle login_page success by wrapping the resulting L{IResource} avatar
    so that the C{logout} callback will be invoked when rendering is
    complete.
    """
    (interface, avatar, logout) = xxx_todo_changeme
    class ResourceWrapper(proxyForInterface(IResource, 'resource')):
      """
      Wrap an L{IResource} so that whenever it or a child of it
      completes rendering, the cred logout hook will be invoked.

      An assumption is made here that exactly one L{IResource} from
      among C{avatar} and all of its children will be rendered.  If
      more than one is rendered, C{logout} will be invoked multiple
      times and probably earlier than desired.
      """

      def getChildWithDefault(self, name, request):
        """
        Pass through the lookup to the wrapped resource, wrapping
        the result in L{ResourceWrapper} to ensure C{logout} is
        called when rendering of the child is complete.
        """
        return ResourceWrapper(self.resource.getChildWithDefault(name, request))

      def render(self, request):
        """
        Hook into response generation so that when rendering has
        finished completely (with or without error), C{logout} is
        called.
        """
        request.notifyFinish().addBoth(lambda ign: logout())
        return super(ResourceWrapper, self).render(request)

    return ResourceWrapper(avatar)


  def _loginFailed(self, result):
    """
    Handle login_page failure by presenting either another challenge (for
    expected authentication/authorization-related failures) or a server
    error page (for anything else).
    """
    if result.check(error.Unauthorized, error.LoginFailed):
      return UnauthorizedResource(self._credentialFactories)
    else:
      print()
      result,
      "HTTPAuthSessionWrapper.getChildWithDefault encountered "
      "unexpected error"
    return ErrorPage(500, None, None)


  def _selectParseHeader(self, header):
    """
    Choose an C{ICredentialFactory} from C{_credentialFactories}
    suitable to use to decode the given I{Authenticate} header.

    @return: A two-tuple of a factory and the remaining portion of the
        header value to be decoded or a two-tuple of C{None} if no
        factory can decode the header value.
    """
    elements = header.split(' ')
    scheme = elements[0].lower()
    for fact in self._credentialFactories:
      if fact.scheme == scheme:
        return (fact, ' '.join(elements[1:]))
    return (None, None)
