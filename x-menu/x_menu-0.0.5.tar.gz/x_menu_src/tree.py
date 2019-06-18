# from .menu import Stack, Application, Text


class Tree:
    root = None
    _subs = []
    _parent = None
    _cursor = 0
    # def __init__(self, parent=None):
        # self._subs = []
        
        # self._parent = parent
        # if not parent and not Tree.root:
            # Tree.root = self

    def __lshift__(self, instance):
        self._subs.append(instance)
        instance._parent = self
    
    def __rshift__(self, instance):
        self._parent = instance
        if Tree.root is self:
            Tree.root = instance
            if self not in instance._subs:
                instance._subs.append(self)

    def __getitem__(self, id):
        return self._subs[id]

        
class Files(Tree):

    def __init__()

# class Tree:

    # def __init__(self, title='some title', parent_list=[]):
        # pass