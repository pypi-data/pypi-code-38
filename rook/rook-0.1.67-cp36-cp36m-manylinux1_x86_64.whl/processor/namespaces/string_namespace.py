import base64

from .namespace import Namespace
from .python_object_namespace import PythonObjectNamespace
from .dumped_primitive_namespace import DumpedPrimitiveNamespace


class StringNamespace(DumpedPrimitiveNamespace):

    def __init__(self, obj, original_size, type, common_type, attributes={}):
        super(StringNamespace, self).__init__(obj, type, common_type, attributes, self.METHODS)
        self.original_size = original_size

    def size(self, args):
        return PythonObjectNamespace(len(self.obj))

    def original_size(self, args):
        return PythonObjectNamespace(self.original_size)

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': self.common_type,
            u'@original_type': self.type,
            u'@original_size' : self.original_size,
            u'@attributes': self.get_attributes_dict(),
            u'@value': self.to_simple_dict(),
            }

    def to_simple_dict(self):
        if self.common_type == 'binary':
            return base64.b64encode(self.obj)
        else:
            return self.obj

    METHODS = (size, original_size)
