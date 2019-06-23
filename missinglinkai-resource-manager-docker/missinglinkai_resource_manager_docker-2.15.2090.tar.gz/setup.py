# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path, environ

import setuptools
import yaml
from setuptools import setup

here = path.abspath(path.dirname(__file__))

long_description = None

if path.isfile(path.join(here, 'README.rst')):
    # Get the long description from the README file
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

package_settings = {}
if path.isfile(path.join(here, 'package-settings.yaml')):
    with open(path.join(here, 'package-settings.yaml'), encoding='utf-8') as f:
        package_settings = yaml.safe_load(f)


def read_requirements(name=None):
    name = 'requirements.txt' if name is None else '{}-requirements.txt'.format(name)
    with open(name) as f:
        return [r for r in f.readlines() if len(r.strip()) > 0 and r.strip()[0] != '#']


def get_dependency_links():
    dependency_links = ['https://pypi.org/simple']
    pip_extra_index_url = environ.get('PIP_EXTRA_INDEX_URL')
    if pip_extra_index_url:
        dependency_links.append(pip_extra_index_url)
    return dependency_links


setup(
    # https://packaging.python.org/specifications/core-metadata/#name
    name=package_settings.get('name', 'missinglinkai_resource_manager_docker'),
    version=package_settings.get('version', '0.0.000001'),
    description=package_settings.get('description', 'MissingLink.ai Resource Manager - Docker version'),
    long_description=long_description,  # Optional
    url=package_settings.get('url', 'https://missinglink.ai'),
    author=package_settings.get('author', 'MissingLink'),
    author_email=package_settings.get('author_email', 'support+rmdocker@missinglink.ai'),
    classifiers=[  # Optional
        'Development Status :: %s' % package_settings.get('classifiers.DevelopmentStatus', '4 - Beta'),
        'Intended Audience :: %s' % package_settings.get('classifiers.IntendedAudience', 'Science/Research'),
        'License :: %s' % package_settings.get('classifiers.License', 'Other/Proprietary License'),
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.6'
    ],
    py_modules=['missinglink.resource_manager.docker'],
    package_data={
        '': ['*.txt', '*.rst', '*.MD§`'],
        'missinglink.resource_manager.docker.controllers.templates': ['*']
    },
    keywords=package_settings.get('keywords', 'missinglink missinglinkai'),  # Optional
    packages=setuptools.find_packages(where='.', exclude=('tests', 'tests*')),
    install_requires=read_requirements(),  # Optional
    python_requires='~=3.6',
    entry_points={  # Optional
        'console_scripts': [
            'ml-rmd=missinglink.resource_manager.docker.cli:main',
        ],
    },
    dependency_links=get_dependency_links(),
)
