
from .python_object_namespace import PythonObjectNamespace
from .dumped_object_namespace import DumpedObjectNamespace


class CodeObjectNamespace(DumpedObjectNamespace):

    def __init__(self, name, module, filename, lineno, type, attributes={}):
        super(CodeObjectNamespace, self).__init__(type, u'code', attributes, self.METHODS)

        self.name = name
        self.module = module
        self.filename = filename
        self.lineno = lineno

    def name(self, args):
        return PythonObjectNamespace(self.name)

    def module(self, args):
        return PythonObjectNamespace(self.module)

    def filename(self, args):
        return PythonObjectNamespace(self.filename)

    def lineno(self, args):
        return PythonObjectNamespace(self.lineno)

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': self.common_type,
            u'@original_type': self.type,
            u'@attributes': self.get_attributes_dict(),
            u'@value': {
                u'name': self.name,
                u'module': self.module,
                u'filename': self.filename,
                u'lineno': self.lineno
            }
        }

    def to_simple_dict(self):
        return '%s @ %s' % (self.name, self.module)

    METHODS = (name, module, filename, lineno)
