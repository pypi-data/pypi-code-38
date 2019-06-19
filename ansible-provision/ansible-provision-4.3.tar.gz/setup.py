from subprocess import *
from setuptools import setup, find_packages
from setuptools.command.install import install
from ansible_provision import __version__
import os

__name__ = 'ansible-provision'

setup(
    name = __name__,
    version = __version__,
    scripts = ['ansible-provision'],
    install_requires = ['ansible-deploy'],
    packages = [__name__.replace("-", "_")],
    url = 'https://www/github.com/moshloop/ansible-provision',
    author = 'Moshe Immerman', author_email = 'moshe.immerman@gmail.com'
)