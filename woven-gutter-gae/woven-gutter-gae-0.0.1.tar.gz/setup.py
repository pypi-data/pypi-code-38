#!/usr/bin/env python

import sys
import os
from setuptools import find_packages


try:
    from notsetuptools import setup
except ImportError:
    from setuptools import setup

tests_require = [
    'nose', 'exam', 'mock', 'django', 'redis'
]

if sys.version_info < (3, 3):
    tests_require.append('unittest2')
    tests_require.append('nose-performance')


setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
    INSTALLED_APPS = ('gutter.client',)
    SECRET_KEY = 'secret!'

if 'flake8' in sys.argv[1:]:
    setup_requires.append('flake8')
    setup_requires.append('dont-fudge-up')

setup(
    name='woven-gutter-gae',
    version='0.0.1',
    author='DISQUS, soulhave',
    author_email='opensource@disqus.com, soulhave@yahoo.com.br',
    url='https://github.com/soulhave/woven-gutter-gae',
    description='Client to gutter feature switches backend, '
                'using GCP (Datastore and appengine)',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
        'durabledict>=0.9.0',
        'jsonpickle',
        'werkzeug',
        'six',
        'flask>=1.0.3',
        'flask-restplus>=0.12.1',
        'google-cloud-logging>=1.11.0',
        'google-cloud-datastore>=1.8.0'
    ],
    setup_requires=setup_requires,
    namespace_packages=['gutter'],
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
