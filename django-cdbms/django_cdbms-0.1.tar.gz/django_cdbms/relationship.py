import sys

from past.types import basestring

from .lib import import_module
from .manager import RelationalManager, GraphManager, DocumentManager

INNER = 0
OUTER = 1


class CrossDBRelationship:

    def __init__(self, _raw_class,
                 field_name: str,
                 cls_path: str,
                 strategy: int,
                 related: bool = False,
                 manager=RelationalManager):

        super().__init__(cls_path, field_name)
        self._raw_class = _raw_class
        self.module_name = sys._getframe(4).f_globals['__name__']
        self.manager = manager
        self.definition = {
            'field_name': field_name,
            'related': related,
            'strategy': strategy
        }
        if '__file__' in sys._getframe(4).f_globals:
            self.module_file = sys._getframe(4).f_globals['__file__']

        self.target_class = self._lookup_target_class()

    def _lookup_target_class(self):
        if not isinstance(self._raw_class, basestring):
            return self._raw_class
        else:
            name = self._raw_class
            if name.find('.') == -1:
                module = self.module_name
            else:
                module, _, name = name.rpartition('.')

            if module not in sys.modules:
                # yet another hack to get around python semantics
                # __name__ is the namespace of the parent module for __init__.py files,
                # and the namespace of the current module for other .py files,
                # therefore there's a need to define the namespace differently for
                # these two cases in order for . in relative imports to work correctly
                # (i.e. to mean the same thing for both cases).
                # For example in the comments below, namespace == myapp, always
                if not hasattr(self, 'module_file'):
                    raise ImportError("Couldn't lookup '{0}'".format(name))

                if '__init__.py' in self.module_file:
                    # e.g. myapp/__init__.py -[__name__]-> myapp
                    namespace = self.module_name
                else:
                    # e.g. myapp/models.py -[__name__]-> myapp.models
                    namespace = self.module_name.rpartition('.')[0]

                # load a module from a namespace (e.g. models from myapp)
                if module:
                    module = import_module(module, namespace).__name__
                # load the namespace itself (e.g. myapp)
                # (otherwise it would look like import . from myapp)
                else:
                    module = import_module(namespace).__name__
            return getattr(sys.modules[module], name)

    def build_cross_manager(self, source, name):
        return self.manager(source,
                            name,
                            self.definition,
                            self.target_class)


class RelationRelationship(CrossDBRelationship):

    def __init__(self,
                 _raw_class,
                 field_name: str,
                 cls_path: str,
                 strategy: int,
                 related: bool = False,
                 manager=RelationalManager):
        super().__init__(_raw_class, field_name, cls_path, strategy, related, manager)


class GraphRelationship(CrossDBRelationship):
    def __init__(self,
                 _raw_class,
                 field_name: str,
                 cls_path: str,
                 strategy: int,
                 related: bool = False,
                 manager=GraphManager):
        super().__init__(_raw_class, field_name, cls_path, strategy, related, manager)


class DocumentRelationship(CrossDBRelationship):
    def __init__(self,
                 _raw_class,
                 field_name: str,
                 cls_path: str,
                 strategy: int,
                 related: bool = False,
                 manager=DocumentManager):
        super().__init__(_raw_class, field_name, cls_path, strategy, related, manager)
