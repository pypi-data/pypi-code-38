
from .namespace import Namespace


class FormattedNamespace(Namespace):

    def __init__(self, string):
        super(FormattedNamespace, self).__init__()
        self.obj = string

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': Namespace.__name__,
            u'@value': self.obj,
            }

    def to_simple_dict(self):
        return self.obj
