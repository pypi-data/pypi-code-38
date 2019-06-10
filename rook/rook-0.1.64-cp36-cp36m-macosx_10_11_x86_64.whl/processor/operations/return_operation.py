
class Return(object):

    def __init__(self, arguments, factory):
        self._path = factory.get_path(arguments['path'])

    def execute(self, namespace):
        return self._path.read_from(namespace)
