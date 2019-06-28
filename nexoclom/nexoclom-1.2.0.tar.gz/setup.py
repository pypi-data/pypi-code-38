#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
import glob
import os
import subprocess
import sys
from setuptools import setup, find_packages, Extension, Command
from setuptools.command.test import test as TestCommand

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

# Get some values from the setup.cfg
conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'nexoclom')
DESCRIPTION = metadata.get('description', '')
AUTHOR = metadata.get('author', 'Matthew Burger')
AUTHOR_EMAIL = metadata.get('author_email', 'mburger@stsci.edu')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'unknown')
__minimum_python_version__ = metadata.get("minimum_python_version", "3.7")

# if os.path.exists('relic'):
#     sys.path.insert(1, 'relic')
#     import relic.release
# else:
#     try:
#         # Note: This is the way this will work
#         import relic.release
#     except ImportError:
#         try:
#             subprocess.check_call(['git', 'clone',
#                                    'https://github.com/jhunkeler/relic.git'])
#             sys.path.insert(1, 'relic')
#             import relic.release
#         except subprocess.CalledProcessError as e:
#             print(e)
#             exit(1)

#version = relic.release.get_info()
#relic.release.write_template(version, PACKAGENAME)
for line in open(f'{PACKAGENAME}/__init__.py', 'r').readlines():
    if 'version' in line:
        version = line.split('=')[1].strip().replace("'", "").replace('"', '')


# allows you to build sphinx docs from the pacakge
# main directory with python setup.py build_sphinx
try:
    from sphinx.cmd.build import build_main
    from sphinx.setup_command import BuildDoc

    class BuildSphinx(BuildDoc):
        """Build Sphinx documentation after compiling C source files"""

        description = 'Build Sphinx documentation'

        def initialize_options(self):
            BuildDoc.initialize_options(self)

        def finalize_options(self):
            BuildDoc.finalize_options(self)

        def run(self):
            build_cmd = self.reinitialize_command('build_ext')
            build_cmd.inplace = 1
            self.run_command('build_ext')
            build_main(['-b', 'html', './docs', './docs/_build/html'])

except ImportError:
    class BuildSphinx(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            print('!\n! Sphinx is not installed!\n!', file=sys.stderr)
            exit(1)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['nexoclom/tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


readme_glob = 'README*'
if os.path.exists('LONG_DESCRIPTION.rst'):
    with open('LONG_DESCRIPTION.rst') as f:
        LONG_DESCRIPTION = f.read()
elif len(glob.glob(readme_glob)) > 0:
    with open(glob.glob(readme_glob)[0]) as f:
        LONG_DESCRIPTION = f.read()
else:
    # Get the long description from the package's docstring
    __import__(PACKAGENAME)
    package = sys.modules[PACKAGENAME]
    LONG_DESCRIPTION = package.__doc__

setup(name=PACKAGENAME,
      version=version,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      install_requires= [s.strip() for s in
                 metadata.get('install_requires', 'astropy').split(',')],
      python_requires='>={}'.format(__minimum_python_version__),
          tests_require=['pytest'],
          packages=find_packages(),
          package_data={PACKAGENAME:
                        ['data/g-values/*.dat',
                         'data/Loss/Photo/*.dat']},
          include_package_data=True,
          cmdclass={
              'test': PyTest,
              'build_sphinx': BuildSphinx},
)
