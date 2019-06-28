
class ScopeGuard:
    def __init__(self, handler):
        self.handler = handler

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.handler()
