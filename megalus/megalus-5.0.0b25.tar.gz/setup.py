"""Setup.py main file."""
import os
from codecs import open
from os import path
from setuptools import setup, find_packages
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip
from megalus import __version__

here = path.abspath(path.dirname(__file__))

pfile = Project(chdir=False).parsed_pipfile
package_requirements = convert_deps_to_pip(pfile['packages'], r=False)
dev_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

if os.getenv('USE_DEV_DEPS'):
    print("Installing dev-packages...")
    full_requirements = package_requirements + dev_requirements
else:
    full_requirements = package_requirements

requirements = [
    req
    for req in full_requirements
    if not req.startswith("http")
]


# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='megalus',
    version=__version__,
    description='Command line helpers for docker and docker-compose',
    long_description=long_description,
    author='Chris Maillefaud',
    include_package_data=True,
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='aws deploy docker npm redis memcached bash',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'meg=megalus.cmd:start'
        ],
    },
)
