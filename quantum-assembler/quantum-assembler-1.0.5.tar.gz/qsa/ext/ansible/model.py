import collections.abc
import collections
import os

import ioc
import ioc.loader
import yaml

from qsa.lib.datastructures import DTO


class Role:
    """Main class for projects that represent a single Ansible
    role.
    """

    def __init__(self, template, basedir='.'):
        self.template = template
        self.basedir = basedir
        self.tasks = TaskManager(self, template)

    def abspath(self, path):
        """Return the absolute path relative to the role base
        directory.
        """
        return os.path.join(self.basedir, path)


class BaseTask:
    pass


class PlaybookManager:

    def abspath(self, path):
        path = str.replace(path, '.', os.sep)
        return os.path.join(self.basedir, path)

    def __init__(self, template, basedir):
        self.template = template
        self.basedir = basedir

    def get(self, namespace, *args, **kwargs):
        """Return a :class:`Playbook` instance representing the given
        `namespace`.
        """
        path = self.abspath(namespace)
        return Playbook.fromfile(f"{path}.yml", *args, **kwargs)


class Playbook:
    serialize = lambda self, x: yaml.safe_dump(x, indent=2,
        default_flow_style=False)

    @classmethod
    def fromfile(cls, fn, **defaults):
        """Deserialize the playbook from YAML and create a new
        :class:`Playbook` instance.
        """
        defaults.setdefault('hosts', 'localhost')
        defaults.setdefault('run_once', True)
        plays = [DTO.fromdict(defaults)]
        try:
            with open(fn) as f:
                buf = f.read()
            plays = yaml.safe_load(buf)
        except FileNotFoundError:
            pass
        assert len(plays) == 1, fn
        play = DTO.fromdict(plays[0])
        return cls(play, src=fn)

    def __init__(self, spec, src):
        self._src = src
        self._spec = spec
        self._tasks = TaskStatements(spec.get('tasks') or [])

    def add(self, task):
        """Adds a :class:`Task` to the playbook."""
        self._tasks.add(task)

    def task(self, namespace, name, cls=None):
        """Return the task identified by `name` and `namespace`
        or add it to the :class:`Playbook` if it does not
        exist.
        """
        t = self._tasks.get(namespace, name)
        if t is None and cls:
            t = cls(self, namespace, name, src=None)
            self._tasks.add(t)
        elif t is None:
            t = RawTask(DTO())
        return t

    def dump(self):
        """Dumps the playbook to a Python dictionary."""
        self._spec.tasks = self._tasks.dump(as_task=True)
        return [self._spec]

    def persist(self, codebase):
        """Persists the playbook to disk."""
        buf = '---\n'
        buf += self.serialize(self.dump())
        dirname = os.path.dirname(self._src)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        codebase.write(self._src, str.strip(buf))

    def render(self, template):
        """Renders the playbook to a YAML-encoded string."""
        print(yaml.safe_dump(self.dump(), indent=2, default_flow_style=False))


class TaskManager:
    serialize = lambda self, x: yaml.safe_dump(x, indent=2,
        default_flow_style=False)

    def __init__(self, role, template):
        self.role = role
        self.template = template

    def abspath(self, namespace, name):
        """Return the absolute path to the task identified by the
        namespace and name.
        """
        return self.role.abspath(
            str.replace(f"tasks/{namespace}.yml", ":", os.sep))

    def get(self, namespace, name, cls):
        fn = self.abspath(namespace, name)
        if not os.path.exists(fn):
            task = cls(self, namespace, name, src=fn)
        else:
            stmts = TaskStatements.load(self, fn)
            task = stmts.get(namespace, name)\
                or cls(self, namespace, name, src=fn)
        return task

    def persist(self, codebase, task):
        """Read the YAML containing the task namespace and append
        or replace the task.
        """
        fn = self.role.abspath(os.path.join('tasks', task.filename))
        dirname = os.path.dirname(fn)
        stmts = []

        # TODO: Use TaskStatements.load()
        if os.path.exists(fn):
            stmts = list(map(DTO.fromdict, yaml.safe_load(open(fn))))
        for i, stmt in enumerate(stmts):
            TaskImpl = ioc.loader.import_symbol(stmt.tags[0])
            stmts[i] = TaskImpl.load(self, stmt)
        tasks = TaskStatements(stmts)
        tasks.add(task)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        codebase.write(fn, tasks.render(self.template))

        # Update all paths in the hierarchy.
        self.persist_includes(codebase, 'tasks', includes=[])

    def persist_includes(self, codebase, dirname, depth=-1, basedir=None, includes=None):
        """Walk the directory tree and update all includes."""
        depth += 1
        if basedir is None:
            basedir = dirname
        for path in os.listdir(dirname):
            if depth == 0 and path.endswith('main.yml'):
                continue
            fn = os.path.join(dirname, path)
            if os.path.isfile(fn):
                include = str.replace(fn, basedir, '')\
                    .lstrip(os.sep)
            elif os.path.isdir(fn):
                self.persist_includes(codebase, fn, depth, basedir=basedir,
                    includes=includes)
                continue
            else:
                raise RuntimeError(f"Directory tree corrupted by {fn}")
            ns = str.replace(f"{include}", os.sep, ':')\
                .lstrip(os.sep)\
                .rstrip('.yml')
            includes.append([{
                'include_tasks': include,
                'name': f"Include tasks from namespace {ns}"
            }])

        if depth == 0:
            buf = '---\n'
            buf += '\n'.join([self.serialize(x) for x in includes])
            codebase.write(os.path.join(basedir, 'main.yml'), buf)


class RawTask:
    """A task as it was parsed from the playbook."""

    @property
    def tags(self):
        return self.stmt.tags

    def __init__(self, stmt):
        self.stmt = DTO.fromdict(stmt)

    def isnew(self):
        return not bool(self.stmt)

    def dump(self, *args, **kwargs):
        """Dumps the :class:`RawTask` to a dictionary."""
        return self.stmt

    def render(self, template):
        """Renders the task to YAML that can be executed by
        Ansible.
        """
        return template.render_to_string(Task.template_name,
            task=self.dump())


class Tags:
    """Parses the tags into a dictionary."""

    @property
    def task_qualname(self):
        return self.get('qualname',
            'meta.quantumframework.org')

    def __init__(self, tags, domain=None):
        self.domain = domain
        self.tags = collections.defaultdict(dict)
        for t in tags:
            key, value = str.split(t, ':', 1)
            domain, key = str.split(key, '/', 1)
            if key in self.tags[domain]:
                if isinstance(self.tags[domain][key], str):
                    self.tags[domain][key] = [ self.tags[domain][key] ]
                self.tags[domain][key].append(value)
            else:
                self.tags[domain][key] = value

    def get(self, key, domain=None):
        """Return the given key from the tags."""
        domain = domain or self.domain
        if domain is None:
            raise ValueError("Provide the `domain` parameter or set default.")
        return self.tags.get(domain, {}).get(key)

    def get_task_impl(self):
        """Return the concrete :class:`Task` implementation
        based on the metadata in the tags.
        """
        qualname = self.get('task-impl',
            'ansible.quantumframework.org')
        if not qualname:
            raise LookupError("ansible.quantumframework.org/task-impl not defined in tags.")
        return ioc.loader.import_symbol(qualname)

    def __iter__(self):
        for domain in self.tags:
            for key in self.tags[domain]:
                yield self.tags[domain][key]


class TaskStatements(collections.abc.MutableSet):

    @classmethod
    def load(cls, manager, fp):
        """Load the tasks from the specified filepath `fp`."""
        stmts = list(map(DTO.fromdict, yaml.safe_load(open(fp))))
        for i, stmt in enumerate(stmts):
            TaskImpl = ioc.loader.import_symbol(stmt.tags[0])
            stmts[i] = TaskImpl.load(manager, stmt)
        return cls(stmts)

    def __init__(self, stmts):
        self.__stmts = self.tasks = collections.OrderedDict()
        for stmt in stmts:
            # WARNING: The second tag is considered to be the qualified
            # name of the task (FIXME).
            tags = Tags(stmt.tags)
            self.__stmts[tags.task_qualname] = RawTask(stmt)

    def dump(self, *args, **kwargs):
        """Represents the statements as a list of dictionaries."""
        return [x.dump(*args, **kwargs) for x in self.__stmts.values()]

    def add(self, task):
        """Add or update a task."""
        self[task.qualname] = task

    def get(self, namespace, name):
        """Return the class:`Task` identified by `namespace`
        and `name`.
        """
        try:
            return self[f"{namespace}:{name}"]
        except KeyError:
            return None

    def discard(self, task):
        del self[task.qualname]

    def render(self, template):
        """Renders all tasks to YAML."""
        buf = '---\n'
        return buf + '\n\n\n'.join([x.render(template)
            for x in self.__stmts.values()])

    def __setitem__(self, qualname, task):
        return self.__stmts.__setitem__(qualname, task)

    def __getitem__(self, qualname):
        return self.__stmts[qualname]

    def __delitem__(self, qualname):
        del self.__stmts[qualname]

    def __len__(self):
        return len(self.__stmts)

    def __contains__(self, task):
        return task.qualname in self.__index

    def __iter__(self):
        return iter(self.stmts)


class Task(BaseTask):
    template_name = 'ci/ansible/task.yml.j2'
    empty = object()
    codebase = ioc.class_property('core:CodeRepository')

    @property
    def classname(self):
        return '.'.join([
            self.__module__,
            type(self).__name__
        ])

    @property
    def namespace(self):
        return f'deployment.quantumframework.org/namespace:{self.ansible_ns}'

    @property
    def qualname(self):
        return f'{self.ansible_ns}.{self.name}'

    @property
    def filename(self):
        return self.namespace.replace(':', os.sep) + '.yml'

    @classmethod
    def fromfilepath(cls, manager, fp):
        """Create a new :class:`Task` instance from the Ansible
        tasks in the YAML-encode file at absolute path `fp`.
        """
        if os.path.exists(fp):
            raise NotImplementedError
        return cls(manager, src=fp)

    @classmethod
    def load(cls, playbook, stmt):
        """Load an Ansible task to a corresponding :class:`Task`
        object.
        """
        namespace, name = str.rsplit(stmt.tags[1], ':', 1)
        return cls(playbook, namespace, name, None, stmt=stmt)

    def __init__(self, playbook, namespace, name, src, stmt=None, module=None, _created=False):
        """Initialize a new :class:`Task` instance.

        Args:
            playbook: a :class:`Playbook` instance.
            src (string): the absolute filepath to the
                final :class:`Task` definition.
        """
        self._created = _created
        self.playbook = playbook
        self.name = name
        self.src = src
        self.stmt = stmt
        self.params = {}
        if self.stmt:
            self.params = self.stmt[self.module]
        self.task_name = name
        self.conditions = []
        self.state = self.empty
        self.tags = []

        # If there are parameters, this task is already persisted.

        # This is important - add the qualified name as a tag so we can find
        # the deployment later.
        NS_NS = "deployment.quantumframework.org/qualname"
        self.tag(f'ansible.quantumframework.org/task-impl:{self.classname}')
        self.tag(f'meta.quantumframework.org/version:1.0')
        self.tag(f'meta.quantumframework.org/namespace:{namespace}')
        self.tag(f'ansible.quantumframework.org/qualname/{self.qualname}')
        if self.stmt:
            self.task_name = self.stmt.name
            self.tags = list(sorted(set(stmt.tags) | set(self.tags)))

    def isunbound(self):
        """Return a boolean indicating if the :class:`Task`
        is not bound to a specific environment.
        """
        return 'deployment.quantumframework.org/env:global' in self.tags

    def getplaybook(self, playbooks, force_playbook=None):
        """Return the playbook in which this task belongs."""
        return playbooks.get(force_playbook or self.ansible_ns)

    def tag(self, tag):
        """Adds a tag to the :class:`Task`."""
        if tag not in self.tags:
            self.tags.append(tag)

    def isnew(self):
        """Return a boolean indicating if the object is new."""
        return bool(self._created)

    def predump(self):
        """Invoked prior to dumping the task to a dictionary."""
        pass

    def dump(self, as_task=False):
        """Return a dictionary representing the Ansible task."""
        self.predump()
        assert self.params
        assert self.module
        stmt = {
            'name': self.task_name,
            '__params__': self.params,
            'tags': list(sorted(set(self.tags))),
            '__module__': self.module
        }
        if self.conditions:
            stmt['when'] = ' and '.join(self.conditions)
        if self.state != self.empty:
            stmt['__params__']['state'] = self.state
        if as_task:
            stmt[stmt.pop('__module__')] = stmt.pop('__params__')
        return stmt

    def setname(self, name):
        """Sets the name of the task in the Ansible playbook."""
        self.task_name = name

    def when(self, stmt):
        """Execute the task conditionally."""
        self.conditions.append(stmt)

    def render(self, template):
        """Renders the task to YAML that can be executed by
        Ansible.
        """
        return template.render_to_string(self.template_name,
            task=self.dump())

    def persist(self):
        """Persists the task to disk."""
        self.playbook.persist(self)
