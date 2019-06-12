import os, subprocess
from pathlib import Path
from setuptools.command.install import install
from distutils.spawn import find_executable

from .main import run

BASH_LOGIN_FILES = ['~/.bash_profile', '~/.bash_login', '~/.profile', '~/.bashrc']


class CustomInstall(install):
    def get_bash_file(self):
        paths = [Path(_).expanduser() for _ in BASH_LOGIN_FILES]
        result = [_ for _ in paths if os.path.exists(_) and os.path.isfile(_) and os.access(_, os.R_OK)]
        if not result:
            open('~/.bash_profile', 'w').close()
            result = [Path('~/.bash_profile').expanduser()]
        return result[0]

    def get_zsh_file(self):
        z_dot_dir = os.environ.get('ZDOTDIR', '~')
        zsh_file = Path(f'{z_dot_dir}/.zshenv')
        if not os.path.exists(zsh_file) and os.path.isfile(zsh_file):
            open(zsh_file, 'w').close()
        return zsh_file

    def run(self):
        install.run(self)
        if find_executable('bash'):
            bash_file = self.get_bash_file()
            run('bash', bash_file, bash_file)
        if find_executable('zsh'):
            zsh_file = self.get_zsh_file()
            run('zsh', zsh_file, zsh_file)
        if find_executable('powershell'):
            (powershell_file, _) = subprocess.Popen(["powershell", "$profile"], stdout=subprocess.PIPE, shell=True).communicate()
            powershell_file = str(powershell_file.decode('ascii')).replace('\r\n', '')
            run('powershell', None, powershell_file)
