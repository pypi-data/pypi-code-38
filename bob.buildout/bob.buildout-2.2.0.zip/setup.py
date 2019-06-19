#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 09:49:00 CEST

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

def load_requirements(f):
  retval = [str(k.strip()) for k in open(f, 'rt')]
  return [k for k in retval if k and k[0] not in ('#', '-')]

setup(
    name='bob.buildout',
    version=version,
    description="A collection of zc.buildout recipes for Bob packages",
    keywords=['buildout', 'sphinx', 'nose', 'recipe', 'eggs', 'bob'],
    url='https://gitlab.idiap.ch/bob/bob.buildout',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements('requirements.txt'),

    entry_points = {
      'zc.buildout': [
        'develop = bob.buildout.develop:Recipe',
        'scripts = bob.buildout.scripts:Recipe',
        'python = bob.buildout.scripts:PythonInterpreter',
        'gdb-python = bob.buildout.scripts:GdbPythonInterpreter',
        'ipython = bob.buildout.scripts:IPythonInterpreter',
        'pylint = bob.buildout.scripts:PyLint',
        'nose = bob.buildout.scripts:NoseTests',
        'coverage = bob.buildout.scripts:Coverage',
        'sphinx = bob.buildout.scripts:Sphinx',
        'egg.scripts = bob.buildout.scripts:UserScripts',
        ],
      'zc.buildout.extension': [
        'extension = bob.buildout.extension:extension',
        ],
      },

    classifiers=[
      'Framework :: Bob',
      'Development Status :: 5 - Production/Stable',
      'Environment :: Plugins',
      'Framework :: Buildout :: Recipe',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      ],

    )
