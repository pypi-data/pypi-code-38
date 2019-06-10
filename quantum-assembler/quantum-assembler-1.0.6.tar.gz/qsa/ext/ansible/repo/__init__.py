from .playbook import Playbook


class TaskRepository:
    """Provides persistance abstraction for Ansible
    task objects.
    """

    def __init__(self, basedir='ops/ansible'):
        self.basedir = basedir

    def get(self, cls, name):
        """Retrieve a task from the repository using the
        provided implementation class `cls`.
        """
        p = Playbook.load(self.basedir, cls.ansible_ns)
        return p.get(cls, f'{cls.ansible_ns}.{name}')

    def add(self, task, namespace=None):
        """Adds a new task to the repository."""
        p = Playbook.load(self.basedir, namespace or task.ansible_ns)
        p.persist(task)

    persist = add
