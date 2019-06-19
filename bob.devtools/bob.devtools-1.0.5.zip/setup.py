#!/usr/bin/env python

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

requires = [
    'setuptools',
    'click>=7',
    'click-plugins',
    'conda>=4,<5',
    'conda-build>=3,<4',
    'conda-verify>=3,<4',
    'certifi',
    'requests',
    'gitpython',
    'python-gitlab',
    'sphinx',
    'pyyaml>=5.1',
    'twine',
    'lxml',
    'jinja2',
    'termcolor',
    'psutil',
    ]

setup(
    name="bob.devtools",
    version=version,
    description="Tools for development and CI integration of Bob/BEAT packages",
    url='http://gitlab.idiap.ch/bob/bob.devtools',
    license="BSD",
    author='Bob/BEAT Developers',
    author_email='bob-devel@googlegroups.com,beat-devel@googlegroups.com',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    # when updating these dependencies, update the README too
    install_requires=requires,

    entry_points={
        'console_scripts': [
            'bdt = bob.devtools.scripts.bdt:main',
        ],
        'bdt.cli': [
          'new = bob.devtools.scripts.new:new',
          'dumpsphinx = bob.devtools.scripts.dumpsphinx:dumpsphinx',
          'create = bob.devtools.scripts.create:create',
          'build = bob.devtools.scripts.build:build',
          'rebuild = bob.devtools.scripts.rebuild:rebuild',
          'test = bob.devtools.scripts.test:test',
          'caupdate = bob.devtools.scripts.caupdate:caupdate',
          'ci = bob.devtools.scripts.ci:ci',
          'gitlab = bob.devtools.scripts.gitlab:gitlab',
          ],

        'bdt.gitlab.cli': [
          'commitfile = bob.devtools.scripts.commitfile:commitfile',
          'release = bob.devtools.scripts.release:release',
          'changelog = bob.devtools.scripts.changelog:changelog',
          'lasttag = bob.devtools.scripts.lasttag:lasttag',
          'runners = bob.devtools.scripts.runners:runners',
          'jobs = bob.devtools.scripts.jobs:jobs',
          'visibility = bob.devtools.scripts.visibility:visibility',
          'getpath = bob.devtools.scripts.getpath:getpath',
          ],

        'bdt.ci.cli': [
          'base-build = bob.devtools.scripts.ci:base_build',
          'build = bob.devtools.scripts.ci:build',
          'test = bob.devtools.scripts.ci:test',
          'clean = bob.devtools.scripts.ci:clean',
          'base-deploy = bob.devtools.scripts.ci:base_deploy',
          'deploy = bob.devtools.scripts.ci:deploy',
          'readme = bob.devtools.scripts.ci:readme',
          'pypi = bob.devtools.scripts.ci:pypi',
          'nightlies = bob.devtools.scripts.ci:nightlies',
          'docs = bob.devtools.scripts.ci:docs',        
          ],

    },
    classifiers=[
        'Framework :: Bob',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
    ],
)
