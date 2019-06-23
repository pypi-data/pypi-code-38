class Route:
    BASE = 'https://typetalk.com'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        self.url = '{}{}'.format(self.BASE, self.path)

    @property
    def bucket(self):
        return '{0.method}:{0.path}'.format(self)
