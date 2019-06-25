import json
import subprocess


class StackUpdateError(Exception):
    pass


class Stack:
    def __init__(self, kubectl, name):
        self.kubectl = kubectl
        self.name = name

    def annotate_restart(self, restart_id):
        patch = [{'op': 'add', 'path': '/spec/podTemplate/metadata/annotations', 'value': {'restart': restart_id}}]
        command = self.kubectl.cmdline('patch', 'stack', self.name,
                                       '--type', 'json',
                                       '--patch', '{}'.format(json.dumps(patch)))
        try:
            subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise StackUpdateError('Failed to add annotations to pod template: %s'.format(e.stderr))
