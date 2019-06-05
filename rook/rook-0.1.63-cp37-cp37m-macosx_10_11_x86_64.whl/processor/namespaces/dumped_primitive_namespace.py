import datetime

from .dumped_object_namespace import DumpedObjectNamespace

from .python_object_namespace import PythonObjectNamespace


class DumpedPrimitiveNamespace(DumpedObjectNamespace):

    def __init__(self, obj, type, common_type, attributes={}, methods=()):
        super(DumpedPrimitiveNamespace, self).__init__(type, common_type, attributes, methods)
        self.obj = obj

    def _get_value_for_json(self):
        if isinstance(self.obj, complex):
            return {u'real': self.obj.real, u'imag': self.obj.imag}
        elif isinstance(self.obj, datetime.datetime):
            return str(self.obj)
        else:
            return self.obj

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': self.common_type,
            u'@original_type': self.type,
            u'@attributes' : self.get_attributes_dict(),
            u'@value': self._get_value_for_json(),
            }

    def to_simple_dict(self):
        return self._get_value_for_json()

    def __hash__(self):
        return hash(self.obj)
