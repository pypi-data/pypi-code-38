EMPTY = object()


class AbstractRoleBinding:
    defaults = {'subjects': []}

    @property
    def rules(self):
        return self._manifest.rules

    @property
    def subjects(self):
        return self._manifest.setdefault('subjects', [])

    def addsubject(self, subject):
        """Adds a new subject to the ``ClusterRoleBinding``."""
        self.subjects.append(subject)

    def addsubjectfromresource(self, resource):
        """Adds a new subject to the ``ClusterRoleBinding``."""
        self.subjects.append({
            'kind': resource.kind,
            'name': resource.name
        })

    def popsubject(self, namespace, name, default=EMPTY):
        """Pop a subject from the array and return it."""
        i = self.index(namespace, name)
        try:
            return self.subjects.pop(i)
        except IndexError:
            if default == EMPTY:
                raise
            return default

    def getsubject(self, namespace, name):
        """Get a subject from the binding by its namespace and
        name.
        """
        for sub in self.subjects:
            if not (sub.name == name and sub.namespace == namespace):
                continue
            break
        else:
            raise LookupError(f"No such subject in namespace {namespace}: {subject}")
        return sub

    def setrole(self, role):
        """Sets the ``ClusterRole`` for this binding."""
        self.subjects # TODO
        self.roleref['name'] = role

    def index(self, namespace, name):
        """Return the index of the given subject identified by namespace
        and name.
        """
        for i, sub in enumerate(self.subjects):
            if not (sub.name == name and sub.namespace == namespace):
                continue
            break
        else:
            raise IndexError(f"No such subject in namespace {namespace}: {subject}")
        return i

    def on_bound(self):
        """Ensure that all subjects mentioned in the :class:`RoleBinding`
        have their namespaces prefixed.
        """
        for sub in self.subjects:
            if self.prefix in sub.namespace:
                continue
            sub.namespace = f'{self.prefix}{sub.namespace}'
