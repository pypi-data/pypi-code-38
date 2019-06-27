#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

def _load_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
        return long_description

def _get_requires(filename):
    requirements = []
    with open(filename) as req_file:
        for line in req_file.read().splitlines():
            if not line.strip().startswith("#"):
                requirements.append(line)
    return requirements

def _my_version():
    def empty_scheme(version):
        return ''
    return {'local_scheme': empty_scheme}

setup(
    name='sesame-package-tools',
    use_scm_version=_my_version,
    setup_requires=['setuptools_scm'],
    long_description=_load_long_description(),
    description='Sesame Packaging Tools for building Conan recipes',
    url='https://github.com/birsoyo/sesame-package-tools',
    author='Orhun Birsoy',
    author_email='orhunbirsoy@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=['conan', 'C/C++', 'package', 'libraries', 'developer', 'manager', 'dependency', 'tool', 'c', 'c++', 'cpp'],
    packages=find_packages(exclude=['tests']),
    install_requires=_get_requires(os.path.join('sesame', 'requirements.txt')),
    extras_require={'test': _get_requires(os.path.join('sesame', 'requirements_test.txt'))},
    python_requires='>=3.6',
    package_data={
        '': ['*.md'],
        'sesame' : ['*.txt', 'templates/*', 'conan_settings/*', 'conan_settings/profiles/*'],
    },
    entry_points={
        'console_scripts': [
            'sesame=sesame.sesame:run'
        ]
    }
)
