
from .python_object_namespace import PythonObjectNamespace
from .dumped_object_namespace import DumpedObjectNamespace


class UnknownNamespace(DumpedObjectNamespace):

    def __init__(self, type, attributes={}):
        super(UnknownNamespace, self).__init__(type, "UnknownObject", attributes)

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': self.common_type,
            u'@original_type': self.type,
            u'@attributes': self.get_attributes_dict()
        }

    def to_simple_dict(self):
        return u'<Unknown>'
