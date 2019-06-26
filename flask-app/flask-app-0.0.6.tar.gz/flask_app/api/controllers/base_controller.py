class BaseController(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, *args, **kwargs):
        raise NotImplementedError()

    def put(self, *args, **kwargs):
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, request):
        mapper = {
            "get": self.get,
            "post": self.post,
            "put": self.put,
            "delete": self.delete
        }
        call = mapper.get(request.method.lower())
        return call()
