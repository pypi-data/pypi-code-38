
from masonite.request import Request

from ..helpers import hashid


class HashIDMiddleware:

    def __init__(self, request: Request):
        self.request = request

    def before(self):
        self.request.request_variables = hashid(
            self.request.all(), decode=True)
        self.request.url_params = hashid(self.request.url_params, decode=True)

    def after(self):
        pass
