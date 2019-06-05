
from .namespace import Namespace


class MaxDepthNamespace(Namespace):

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': Namespace.__name__,
            }

    def to_simple_dict(self):
        return '<MaxDepthLimit>'
