import os
import subprocess
from os import path

import toml


class BuildContext:
    def __init__(self, folder_path=None):
        folder_path = path.abspath(folder_path or '.')

        self._path = path.join(folder_path, 'moor.toml')
        self._build_folder = path.dirname(self._path)
        self._parent_folder = path.basename(self._build_folder)

        if not path.exists(self._path):
            raise RuntimeError('Unable to locate build config at: ' + self._path)

        with open(self._path, 'r') as config_file:
            self._cfg = toml.load(config_file)

    @property
    def name(self):
        if 'name' in self._cfg:
            return self._cfg['name']
        else:
            return self._parent_folder

    @property
    def registry(self):
        return self._cfg.get('registry', '')

    @property
    def version(self):

        # early exit if the version has been hard coded
        if 'version' in self._cfg:
            return self._cfg['version']

        # attempt to automatically assign a version using the git describe
        ver = None
        try:
            cmd = ['git', 'describe', '--always', '--dirty=-wip']
            with open(os.devnull, 'w') as null_file:
                ver = subprocess.check_output(cmd, stderr=null_file).decode().strip()
        except subprocess.CalledProcessError:
            # in cases where a version number can't be determined then callback to 'latest'
            ver = 'latest'

        return ver

    @property
    def local_tag(self):
        return '{}:{}'.format(self.name, self.version)

    @property
    def latest_tag(self):
        return '{}:latest'.format(self.name)

    @property
    def remote_tag(self):
        if 'registry' not in self._cfg:
            raise RuntimeError('Registry not set in configuration unable to determine remote tag')

        return '{}/{}'.format(self._cfg['registry'], self.local_tag)

    def build_image(self, local=False):
        tag_name = self.latest_tag if local else self.remote_tag

        cmd = [
            'docker',
            'build',
            '-t', tag_name,
            self._build_folder,
        ]
        subprocess.check_call(cmd)

    def push_image(self):
        cmd = [
            'docker',
            'push',
            self.remote_tag,
        ]
        subprocess.check_call(cmd)
