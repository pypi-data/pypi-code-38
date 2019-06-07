from pylatex.base_classes import Environment, Options

class PyVars(Environment):
    """A pycode environment that assigns values to pythontex variables.

    Each keyword argument defines a pythontex variable of the same name with the same value.

    """

    def __init__(self, **kwargs):
        # Set the optional session name
        #if session:
        #    super().__init__(options=Options(session))
        #else:
        #    super().__init__()
        super().__init__()

        self._latex_name = 'pycode'
        self.content_separator = '\n'
        #self.kwargs = kwargs

        # Append 'key = value' for every keyword argument
        for key, value in kwargs.items():
            self.append(f'{key} = {value}')

    #def dumps(self):
        # Append 'key = value' for every keyword argument
        #for key, value in self.kwargs.items():
        #    self.append(f'{key} = {value}')

        #return super().dumps()