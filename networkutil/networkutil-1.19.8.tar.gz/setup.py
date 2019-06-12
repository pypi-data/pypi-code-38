# encoding: utf-8

import os
import re
from setuptools import setup, find_packages


MODULE_NAME = u'networkutil'  # The module name must match this!

metadata_file = open(os.path.join(MODULE_NAME, u'_metadata.py')).read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*u'([^']+)'", metadata_file))

test_dependencies = []


def read(filename):

    """
    Utility function used to read the README file into the long_description.

    :param filename: Filename to read

    :return: file pointer
    """

    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name=MODULE_NAME,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=metadata.get(u'version'),

    author=metadata.get(u'author'),
    author_email=metadata.get(u'authoremail'),

    license=metadata.get(u'license'),

    url=u'https://{host}/{user}/{repo}'.format(host=metadata.get(u'githost'),
                                               user=metadata.get(u'gituser'),
                                               repo=metadata.get(u'gitrepo')),
    download_url=u'https://{host}/{user}/{repo}/get/{version}.tar'.format(host=metadata.get(u'githost'),
                                                                          user=metadata.get(u'gituser'),
                                                                          repo=metadata.get(u'gitrepo'),
                                                                          version=metadata.get(u'version')),

    packages=find_packages(),

    # If you want to distribute just a my_module.py, uncomment
    # this and comment out packages:
    #   py_modules=["my_module"],

    description=metadata.get(u'description'),
    long_description=read(u'README.rst'),

    keywords=[MODULE_NAME],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project?
        #   Development Status :: 1 - Planning
        #   Development Status :: 2 - Pre-Alpha
        #   Development Status :: 3 - Alpha
        #   Development Status :: 4 - Beta
        #   Development Status :: 5 - Production/Stable
        #   Development Status :: 6 - Mature
        #   Development Status :: 7 - Inactive
        u'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        u'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        u'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 2.7',
        u'Programming Language :: Python :: 3',
        u'Programming Language :: Python :: 3.6',

        u'Topic :: Utilities',
    ],

    # Dependencies
    install_requires=[
        u'pip>=18.1',
        u'attrs>=17.3.0',
        u'requests>=2.7.0',
        u'pyftpdlib>=1.5.2',
        u'scp>=0.10.2',
        u'paramiko>=2.0.2',
        u'netifaces>=0.10.5',
        u'cryptography>=2.2.1',
        u'better-exceptions>=0.1.6',
        u'logging-helper>=1.5.0',
        u'conversionutil>=1.0.0',
        u'classutils>=1.15.1',
        u'configurationutil>=3.0.2',
        u'stateutil>=1.0.8',
        u'uiutil>=1.16.1',
        u'timingsutil>=1.2.0',
        u'pydnserver>=2.2.8',
        u'websocket-client==0.52.0',
        u'ipaddress>=1.0.19',
        u'future>=0.16.0',
        u'fdutil>=1.7.8'
    ],

    tests_require=test_dependencies,

    extras_require={
        u'test': test_dependencies,
        u'sniffer': [
            u'pcapy>=0.11.1'
        ],
    },

    # Reference any non-python files to be included here
    package_data={
        '': ['*.md', '*.rst', '*.db', '*.txt', '*.json'],  # Include all files that contains *.db/*.md/*.txt/*.json
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [],
    },

    # List any scripts that are to be deployed to the python scripts folder
    scripts=[]

)
