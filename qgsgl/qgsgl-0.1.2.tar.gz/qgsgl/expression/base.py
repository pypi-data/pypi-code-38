

class BaseExpression:
    def __init__(self, renderer, prop):
        self.renderer = renderer
        self.prop = prop

    def get_json(self):
        """Implemented by child classes"""

        raise NotImplementedError()
