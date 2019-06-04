class Dep(object):
    def __init__(self, name):
        self.name = name
        self.deps = []

    def resolve(self, resolved=None, unresolved=None):
        if resolved is None:
            resolved = []
        if unresolved is None:
            unresolved = set()

        unresolved.add(self)

        for dep in self.deps:
            if dep not in resolved:
                if dep in unresolved:
                    print("skip dep %s -> %s", self.name, dep.name)
                    continue
                dep.resolve(resolved, unresolved)

        resolved.append(self)
        unresolved.discard(self)

        return resolved
