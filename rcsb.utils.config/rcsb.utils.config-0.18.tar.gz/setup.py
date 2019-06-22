# File: setup.py
# Date: 9-Mar-2018
#
# Update:
#   3-Jul-2018  jdw update CLI entry points and dependencies
#  21-Aug-2018  jdw version adjustments
#  22-Aug-2018  jdw adjust for namespace packaging
#   3-Oct-2018  jdw add 'ruamel.yaml' dependency
#
import re

from setuptools import find_packages
from setuptools import setup

packages = []
thisPackage = 'rcsb.utils.config'

with open('rcsb/utils/config/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name=thisPackage,
    version=version,
    description='RCSB Python Configuration Utilities',
    long_description="See:  README.md",
    author='John Westbrook',
    author_email='john.westbrook@rcsb.org',
    url='https://github.com/rcsb/py-rcsb_utils_config',
    #
    license='Apache 2.0',
    classifiers=(
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
    entry_points={
    },
    #
    install_requires=['future', 'configparser; python_version < "3.0"', 'ruamel.yaml'],
    packages=find_packages(exclude=['rcsb.utils.tests-config', 'rcsb.utils.tests-*', 'tests.*']),
    package_data={
        # If any package contains *.md or *.rst ...  files, include them:
        '': ['*.md', '*.rst', "*.txt", "*.cfg"],
    },
    #
    # These basic tests require no database services -
    test_suite="rcsb.utils.config.tests-config",
    tests_require=['tox'],
    #
    # Not configured ...
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    # Added for
    command_options={
        'build_sphinx': {
            'project': ('setup.py', thisPackage),
            'version': ('setup.py', version),
            'release': ('setup.py', version)
        }
    },
    # This setting for namespace package support -
    zip_safe=False,
)
