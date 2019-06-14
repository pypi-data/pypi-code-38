#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""setuptools script of this package

see:

* https://packaging.python.org/
* https://setuptools.readthedocs.io/
"""

from setuptools import find_packages as find, setup

setup(
    name='ks33requests',
    description='适用于金山云对象存储(KS3)的简单 Python3 客户端',
    url='https://github.com/tanbro/ks33requests',
    packages=find('src'),
    package_dir={'': 'src'},
    use_scm_version={
        # guess-next-dev:	automatically guesses the next development version (default)
        # post-release:	generates post release versions (adds postN)
        'version_scheme': 'guess-next-dev',
        'write_to': 'src/ks33requests/_scm_version.py',
    },
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
    author='liu xue yan',
    author_email='liu_xue_yan@foxmail.com',
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    install_requires=[
        'requests',
        'lxml',
    ],
    tests_require=[
        'python-dotenv',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
