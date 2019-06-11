#! /usr/bin/env python
from setuptools import setup, find_packages
import os

def get_version():
    filename = os.path.join('fussy','version.py')
    if not os.path.exists(filename):
        return '1.0.0'
    for line in open(filename):
        if line.startswith( '__version__' ):
            return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError( "Unable to determine version" )

if __name__ == "__main__":
    setup(
        name='fussy',
        version=get_version(),
        description='Field-Upgradable Software Support',
        long_description='''Fussy Software Packager

Fussy provides a collection of tools to create field-upgraded
software installations. The installation uses a "pivot" root
on your regular file system into which the current release of 
your software is installed, and which can exist alongside a
number of other versions of the software.

It assumes a Linux-like operating system and requires certain
linux services and utilities for many of its functions.

Notable functionality:

* GPG signed/verified firmware packing and unpacking
* inotify support
* non-blocking process IO (nbio)
* transactional write operation
* process control operations (e.g. kill-kill-kill)
* simple structured log server
* cron locks
''',
        classifiers=[
            "Programming Language :: Python",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        ],
        license="LGPL",
        author='Mike C. Fletcher',
        author_email='mcfletch@vrplumber.com',
        url='http://www.vrplumber.com',
        keywords='firmware,field,upgrade,embedding',
        packages=find_packages(),
        include_package_data=True,
        # system-level requirements
        # python2.6+
        # gpg
        # rsync
        # tar
        install_requires=[
            'setuptools',
        ],
        entry_points = dict(
            console_scripts = [
                'fussy-install=fussy.install:main',
                'fussy-install-bytes=fussy.install:install_bytes_main',
                'fussy-clean=fussy.install:clean_main',
                'fussy-unpack=fussy.unpack:main',
                'fussy-pack=fussy.pack:main',
                'fussy-sign=fussy.pack:sign_main',
                'fussy-south-rollback=fussy.southrollback:main',
                'fussy-link-tree=fussy.linktree:main',
                'fussy-log-server=fussy.jsonlogserver:main',
                'fussy-format-log=fussy.jsonlogserver:format_log_main',
                'json-format=fussy.jsonformat:main',
                'fussy-file-watch=fussy.filewatch:main',
                'fussy-jsx-watcher=fussy.jsxwatcher:main',
                'fussy-pack-unattended=fussy.unattendedset:main',
                'fussy-deb-metadata=fussy.unattendedset:metadata_main',
                'fussy-sse-server=fussy.sseserver:main',
                'fussy-sse-client-demo=fussy.sseclient:main',
            ],
        ),
    )
