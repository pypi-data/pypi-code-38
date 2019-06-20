

class DynamicImport(object):
    def __init__(self, o):
        if o is None:
            pass

        self.o = o

    def full_name(self):
        return self.o.__module__ + "." + self.o.__class__.__name__

    @property
    def module(self):
        import sys
        return sys.modules[self.module_name()]

    def module_name(self):
        return self.full_name().split('.')[0]

    def bring(self, import_name):
        mod = self.module

        for m in import_name.split('.'):
            mod = getattr(mod, m)

        return mod
