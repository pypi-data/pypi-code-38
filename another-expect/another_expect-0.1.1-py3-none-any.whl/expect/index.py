from .to import to


class expect:
    def __init__(self, actual):
        self._actual = actual
        self._tests = []
        self.to = to(self)
        self.and_ = self
