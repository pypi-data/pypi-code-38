from __future__ import absolute_import, division, print_function

import os
import sys
import subprocess

from setuptools import setup, find_packages
from codecs import open
from os import path
from hcli_core import package

if sys.argv[-1] == 'publish':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("publishing from a branch other than master is disallowed.")
    os.system("rm -rf dist")
    os.system("python setup.py sdist")
    os.system("twine upload dist/* -r pypi")
    os.system("git tag -a %s -m 'version %s'" % ("hcli_core-" + package.__version__, "hcli_core-" + package.__version__))
    os.system("git push")
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == 'tag':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("tagging from a branch other than master is disallowed.")
    os.system("git tag -a %s -m 'version %s'" % ("hcli_core-" + package.__version__, "hcli_core-" + package.__version__))
    sys.exit()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hcli_core',
    version=package.__version__,
    description='An HCLI connector that can be used to expose any CLI expressed through hypertext command line interface (HCLI) semantics.',
    long_description=long_description,
    url='https://github.com/cometaj2/hcli_core',
    author='Jeff Michaud',
    author_email='cometaj2@comcast.net',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli client server connector hypermedia rest generic development',
    packages=find_packages(exclude=['__pycache__', 'tests']),
    install_requires=[package.dependencies[0]],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'hcli_core=hcli_core.__main__:main',
        ],
    },
)
