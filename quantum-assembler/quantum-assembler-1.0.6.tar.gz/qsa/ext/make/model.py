


class Makefile:
    """Abstracts the construction of the project Makefile."""

    @property
    def variables(self):
        return sorted(self._variables, key=lambda x: x['name'])

    def __init__(self, assembler, spec):
        self.assembler = assembler
        self.spec = spec
        self.targets = {}
        self._variables = []
        assembler.notify('setup_makefile', self)

    def setvariable(self, name, default, export=False):
        """Sets a global variable for the Makefile."""
        self._variables.append({'name': name, 'default': default,
            'export': export})

    def target(self, name):
        """Add a new target to the Makefile and return a
        :class:`Target` instance.
        """
        if name not in self.targets:
            self.targets[name] = Target(self.assembler, self, name)
        return self.targets[name]

    def __iter__(self):
        for k in sorted(self.targets.keys()):
            yield self.targets[k]


class Target:
    """Represents a target in the project Makefile."""

    def __init__(self, assembler, make, name):
        self.assembler = assembler
        self.make = make
        self.name = name
        self.statements = []

        fn = name.replace('-', '_')\
            .replace('/', '_')\
            .replace('.', '_')

        assembler.notify(f'setup_makefile_target', make, self)
        assembler.notify(f'setup_makefile_target_{fn}',
            make, self)

    def execute(self, stmt, ifneq=None, ifdef=None):
        """Instruct the target to execute the specified statement."""
        if isinstance(stmt, (str, list)):
            stmt = BashStatement(stmt, ifneq=ifneq, ifdef=ifdef)
        self.statements.append(stmt)

    def __iter__(self):
        return iter(self.statements)

    def __str__(self):
        return '\n'.join(map(str, self))


class BashStatement:
    """Represents a single bash statement, that may be compiled over
    multiple lines.
    """

    def __init__(self, stmt, ifneq=None, ifdef=None):
        self.stmt = stmt if isinstance(stmt, list) else [stmt]
        self.ifneq = ifneq
        self.ifdef = ifdef

    def __str__(self):
        stmt = '\t' + '\n\t'.join(self.stmt)
        if self.ifneq:
            stmt = f'ifneq ({self.ifneq})\n' + stmt
            stmt += '\nendif'
        elif self.ifdef:
            stmt = f'ifdef {self.ifdef}\n' + stmt
            stmt += '\nendif'
        return stmt
