import glob

import ioc

from qsa.ext.base import BaseExtension
from .model import Role
from .model import Task
from .model import PlaybookManager
from .repo import TaskRepository


class Extension(BaseExtension):
    name = inject = command_name = 'ansible'
    base_dir = 'ops/ansible'
    _playbook_cache = {}
    codebase = ioc.class_property('core:CodeRepository')

    def setup(self, codebase, template):
        """Instantiate the Ansible role for this project."""
        self.template = template
        self.basedir = codebase.abspath('ops/ansible')
        self.role = Role(template, basedir=self.basedir)
        self.repository = None
        self.playbooks = PlaybookManager(template, self.basedir)
        self.provide_class(TaskRepository(self.basedir))

    def handle(self, project, template):
        """Ensure that Ansible configuration files exist and an inventory
        for each environment.
        """
        if not self.quantum.get('project.type', None):
            return

        if not self.codebase.exists('ansible.cfg'):
            with self.codebase.commit("Update Ansible configuration"):
                template.render_to_file('ansible.cfg.j2',
                    'ansible.cfg')
        vault_names = list(glob.glob('./vault/*.aes'))

        with self.codebase.commit("Update Ansible playbooks"):
            import os

            base_dir = 'ops/ansible/tasks'
            includes = []
            os.makedirs(base_dir, exist_ok=True)
            for dirname in os.listdir(base_dir):
                print(base_dir, dirname)
                if not os.path.isdir(os.path.join(base_dir, dirname)):
                    continue
                includes.append({'include_tasks': f'{dirname}/main.yml'})

            template.render_to_file('ci/ansible/tasks/main.yml.j2',
                'ops/ansible/tasks/main.yml', include_tasks=includes)

            # Now do the same for the main playbook.
            name = self.quantum.get('project.type').replace('+', '-')
            template.render_to_file(f'ci/ansible/main.{name}.yml.j2',
                'ops/ansible/main.yml', include_tasks=[{'include_tasks': 'tasks/main.yml'}])

    def on_ansible_required(self, caller):
        """Check if the folder structure is created and if not,
        do so.
        """
        pass

    def playbook(self, namespace, *args, **kwargs):
        """Get or create a playbook with the given name in the given
        namespace.
        """
        return self.playbooks.get(namespace, *args, **kwargs)

    def task(self, namespace, name, cls=Task):
        """Get or create a task by the specified parameters.

        Args:
            namespace (string): specifies the namespace.
            name (string): specifies the name.
            cls (Task): Task implementation class.
        """
        return self.role.tasks.get(namespace=namespace,
            name=name, cls=cls)

    def setenvfromtask(self, namespace, name, task):
        """Set the environments to which the given task is
        executed to the child task.
        """
        source = self.playbooks.get(namespace)\
            .task(namespace, name=name)
        assert not source.isnew(), source.stmt
        for t in [x for x in source.tags if str.startswith(x, 'env:')]:
            task.tag(t)

    def get(self, cls, name, **defaults):
        """Get or create the task identified by the namespace and name."""
        p = self._playbook_cache.get(cls.ansible_ns)
        if p is None:
            self._playbook_cache[cls.ansible_ns] = p = self.playbooks.get(cls.ansible_ns)

        t = p.task(namespace=cls.ansible_ns, name=name, cls=cls)
        t._playbook = p

        # TODO: An ugly hack. Implement better persistence API.
        def persist():
            self.injector.call(t._playbook.persist)

        t.persist = persist
        return t
