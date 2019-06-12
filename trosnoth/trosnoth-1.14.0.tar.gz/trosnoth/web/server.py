import logging
import mimetypes

from django.contrib.staticfiles import finders
from twisted.internet import reactor
from twisted.web import resource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource

from trosnoth.server.wsgi import application


log = logging.getLogger(__name__)


class WSGIRoot(resource.Resource):
    def __init__(self, wsgi, *args, **kwargs):
        resource.Resource.__init__(self)
        self.wsgi = wsgi

    def getChild(self, child, request):
        request.prepath.pop()
        request.postpath.insert(0, child)
        return self.wsgi

    def render(self, request):
        return self.wsgi.render(request)


class DjangoStatic(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        localPath = finders.find(b'/'.join(request.postpath))
        if not localPath:
            return File.childNotFound.render(request)

        return File(localPath).render_GET(request)


def startWebServer(authFactory, port):
    mimetypes.types_map.update({
        '.trosrepl': 'application/octet-stream',
    })

    root = WSGIRoot(
        WSGIResource(reactor, reactor.getThreadPool(), application))
    root.putChild(b'static', DjangoStatic())
    factory = Site(root)
    return reactor.listenTCP(port, factory)
