import inspect as ins
import ujson as json

"""
Show the meta and the info from a method

"""


class DocMethod:
    """
    THIS IS LIKE A DECORATOR,.... MAYBE??
    """

    def __init__(self, *args, **kwargs):
        self.method = args[0]
        self.get_name_args()

    def get_name_args(self):
        if ins.isfunction(self.method):
            self.name_args = self.method.__code__.co_varnames
        elif ins.ismethod(self.method):
            self.name_args = self.method.__func__.__code__.co_varnames

    def __str__(self):
        return self.method.__name__

    def __repr__(self):
        return json.dumps(self.get_all())

    def name(self):
        return self.method.__name__

    def run_method(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def get_args(self):
        return self.name_args

    def getdoc(self):
        return ins.getdoc(self.method)

    def getcomm(self):
        return ins.getcomments(self.method)

    def getcode(self):
        return ins.getsource(self.method)

    def get_all(self):
        return {
            'name': str(self),
            'doc': self.getdoc(),
            'args': self.get_args(),
            'source': self.getcode()
        }
