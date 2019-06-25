import json
import subprocess

from zalando_kubectl.models.stack import Stack


class DeploymentUpdateError(Exception):
    pass


class Deployment:
    def __init__(self, kubectl, name):
        self.kubectl = kubectl
        self.name = name

    def _spec(self):
        command = self.kubectl.cmdline("get", "deployment")
        command.extend([self.name, '-o', 'json'])
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL)
        return json.loads(output)

    def ss_ref(self):
        try:
            deployment = self._spec()
        except subprocess.CalledProcessError:
            raise RuntimeError('Failed to get deployment spec {}'.format(self.name))
        if 'ownerReferences' not in deployment['metadata']:
            return None
        for r in deployment['metadata']['ownerReferences']:
            if r['kind'] == 'Stack':
                return r
        return None

    def get_stackset(self):
        ref = self.ss_ref()
        return Stack(self.kubectl, ref['name'])

    def annotate_restart(self, restart_id):
        patch = [{'op': 'add', 'path': '/spec/template/metadata/annotations', 'value': {'restart': restart_id}}]
        command = self.kubectl.cmdline('patch', 'deployment', self.name,
                                       '--type', 'json',
                                       '--patch', json.dumps(patch))
        try:
            subprocess.check_call(command, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise DeploymentUpdateError('Failed to annotate deployment: %s'.format(e.stderr))
