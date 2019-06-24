from .namespace import Namespace


class DynamicObjectNamespace(Namespace):

    def __init__(self):
        super(DynamicObjectNamespace, self).__init__()

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': "dynamic"
        }

    def to_simple_dict(self):
        return u'<Dynamic>'
