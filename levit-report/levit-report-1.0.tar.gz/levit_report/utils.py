class AbstractIterator:
    def __init__(self, id, document, view):
        self.id = id
        self.view = view
        self.document = document

    def __call__(self):
        for data in self:
            yield data


class StringIterator(AbstractIterator):

    def __iter__(self):
        yield self.view.get_file(self.document, self.id)
