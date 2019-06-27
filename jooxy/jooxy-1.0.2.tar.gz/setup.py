"""
Unofficial Joox Web API
=========================================

    >>> from jooxy import *

Links
`````

* `GitHub repository <https://github.com/ervan0707/jooxy>`_

"""
from __future__ import with_statement
import re, codecs

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open('jooxy/__init__.py') as f:
    version = re.search(r'__version__\s*=\s*\'(.+?)\'', f.read()).group(1)
assert version

with open('README.rst') as f:
    setup(
        name='jooxy',
        packages=['jooxy'],
        version=version,
        license='BSD 3 Clause License',
        author='Ervan R.F',
        author_email='ervanroot@gmail.com',
        url='https://github.com/ervan0707/jooxy',
        description=' Unofficial Joox Web API',
        long_description=f.read(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
        install_requires=[
            'requests'
        ],
    )