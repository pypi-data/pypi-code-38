import os

import ioc
import yaml

from qsa.lib.datastructures import DTO
from .tasklist import TaskList


class Playbook:
    """Wraps the persistence layer of Ansible playbooks."""
    codebase = ioc.class_property('core:CodeRepository')

    @classmethod
    def load(cls, basedir, ns):
        fn = f"{basedir}/{ns.replace('.', '/')}.yml"
        if os.path.exists(fn):
            with open(fn) as f:
                data = yaml.safe_load(f)
            p = cls(fn, DTO.fromdict(data[0]))
        else:
            p = cls(fn, DTO.fromdict({
                'hosts': 'localhost',
                'tasks': []
            }))
        return p

    def __init__(self, src, play):
        self.src = src
        self.tasks = TaskList(play.tasks)
        self.play = play

    def persist(self, task):
        """Writes all tasks in the playbook to disk."""
        self.tasks.add(task)
        self.play.tasks = list(self.tasks)
        self.codebase.write(self.src,
            yaml.safe_dump([self.play], indent=2, default_flow_style=False))

    def get(self, cls, qualname):
        """Return a task from the playbook by its qualified name."""
        return cls.load(self, self.tasks[qualname])
