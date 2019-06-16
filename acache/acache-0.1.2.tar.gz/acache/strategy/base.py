class Base:

    cache = None

    def filter(self):
        raise NotImplementedError('Base should be subclassed and .filter implemented.')

    def set(self, value, *args, **kwargs):
        raise NotImplementedError('Base should be subclassed and .set implemented.')

    def get(self, *args, **kwargs):
        raise NotImplementedError('Base should be subclassed and .set implemented.')
