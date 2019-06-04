#!/usr/bin/env python
# Installs django-timelimit.

import os
import sys
from distutils.core import setup


def long_description():
    """Get the long description from the README"""
    return open(os.path.join(sys.path[0], 'README.rst')).read()


setup(
    author='Erik van Zijst',
    author_email='erik.van.zijst@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
        ],
    description='A Django template tag used to enforce render time limits within templates.',
    download_url='https://bitbucket.org/evzijst/django-timelimit/downloads/django-timelimit-0.1.tar.gz',
    keywords='django debug watchdog timer timelimit timeout interrupt interruptingcow',
    license='MIT',
    long_description=long_description(),
    name='django-timelimit',
    packages=['django_timelimit', 'django_timelimit.templatetags'],
    url='https://bitbucket.org/evzijst/django-timelimit',
    version='0.2-rc1',
)
