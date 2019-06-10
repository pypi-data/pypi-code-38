import glob
import os
import re

import ioc
import yaml


class TaskSequence:
    """Represents a sequence of tasks."""
    codebase = ioc.class_property('core:CodeRepository')
    tasks_dir = 'templates/k8s'

    @classmethod
    def fromdir(self, base_dir, dirname):
        """Read all Kubernetes manifests from the given directory
        and parse the header to create a sequence of tasks.
        """
        tasks = []

    def __init__(self, base_dir, group, tasks_dir=None, template_name=None):
        self.base_dir = base_dir
        self.tasks_dir = tasks_dir or self.tasks_dir
        self.group = group
        self.tasks = []
        self.template_name = template_name

    def render(self):
        """Creates the top-level tasks YAML file for the
        configured group.
        """
        dirname = os.path.join(self.base_dir, 'tasks/k8s')
        dst = os.path.join(dirname, f'{self.group}.yml')
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        tasks_dir = os.path.join(self.base_dir, self.tasks_dir, self.group)
        buf = '---\n# yamllint disable\n'
        for fn in sorted(glob.glob(f'{tasks_dir}/*.yml')):
            task = KubernetesTask.fromfile(fn, self.template_name)
            buf += task.render()
            buf += '\n\n'
        self.codebase.write(dst, buf.rstrip())


class TopLevelTaskSequence:
    """A task sequence that imports from the other
    tasks.
    """
    template = ioc.class_property('template:Extension')
    codebase = ioc.class_property('core:CodeRepository')
    template_name = 'ci/ansible/tasks/ansible.include_tasks.yml.j2'

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.includes = []

    def include_tasks(self, path):
        self.includes.append({
            'include_tasks': path
        })

    def render(self):
        if self.includes:
            buf = self.template.render_to_string(
                self.template_name, includes=self.includes)
            self.codebase.write(os.path.join(self.base_dir, 'main.yml'), buf)


class KubernetesTask:
    pattern = re.compile('^#\sansible\:\s')
    template = ioc.class_property('template:Extension')
    template_name = 'ci/ansible/tasks/k8s.resource.yml.j2'

    @classmethod
    def fromfile(cls, src, template_name=None):
        """Open `src` and read the task from the header."""
        buf = ''
        for line in open(src).readlines():
            if not cls.pattern.match(line):
                continue
            buf += cls.pattern.sub('', line)
        return cls(yaml.safe_load(buf), template_name=template_name)

    def __init__(self, spec, template_name=None):
        self.spec = spec
        self.template_name = template_name or self.template_name

    def dump(self):
        return self.spec

    def render(self):
        return self.template.render_to_string(self.template_name, spec=self.dump())
