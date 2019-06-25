
from masonite.provider import ServiceProvider
from masonite.view import View

from ..helpers import hashid


class HashIDProvider(ServiceProvider):

    wsgi = False

    def register(self):
        pass

    def boot(self, view: View):
        view.share({'hashid': hashid})
