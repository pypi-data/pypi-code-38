
class ErrorsIterator:

    def __init__(self):
        self.errors = []

    def add_error(self,error):
        self.errors.append(error)

    def iterate_errors(self):
        for error in self.errors:
            yield error
