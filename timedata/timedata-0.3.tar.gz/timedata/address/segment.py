class Segment:
    def __init__(self, name):
        self.name = name

    def set(self, root, *value):
        self._set(root, (value[0] if len(value) == 1 else value))


class Attribute(Segment):
    def __init__(self, name):
        if not name.isidentifier():
            raise ValueError('Not a legal identifier', name)
        super().__init__(name)

    def get(self, root):
        return getattr(root, self.name)

    def _set(self, root, value):
        setattr(root, self.name, value)

    def __str__(self):
        return '.%s' % self.name


class Index(Segment):
    def get(self, root):
        return root[self.name]

    def _set(self, root, value):
        root[self.name] = value

    def __str__(self):
        return '[%s]' % self.name


class Call(Segment):
    def __init__(self):
        pass

    def get(self, root):
        return root()

    def set(self, root, *value):
        root(*value)

    def __str__(self):
        return '()'
