from subprocess import *
from setuptools import setup, find_packages
from setuptools.command.install import install
import os

setup(
    name = 'kube-provision',
    version = '0.2',
    scripts = ['kube-provision'],
    install_requires = ['ansible-deploy', 'ansible-provision', 'kubectl-ansible'],
    url = 'https://www/github.com/moshloop/kube-provision',
    author = 'Moshe Immerman', author_email = 'moshe.immerman@gmail.com'
)
