class NoGrapher():
    """This class enables calls without raise any error, for any method."""
    def __getattr__(self, name):
        def method(*args):
            pass
        return method