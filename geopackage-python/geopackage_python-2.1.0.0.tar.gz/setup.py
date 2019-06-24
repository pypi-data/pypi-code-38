from os import path, environ
from os.path import join, abspath, dirname

from setuptools import setup

base_path = dirname(dirname(abspath(__file__)))
requirementPath = join(base_path, 'requirements.txt')
install_requires = []
if path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
        # removing gdal requirement since it is not needed for the packages
        # that are currently being exported. Also makes it less complicated for
        # other users to use
        install_requires.remove("gdal==2.1.0")

with open(join(base_path, 'README.md'), 'r') as fh:
    long_description = fh.read()

import sys

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


if environ.get('CI_COMMIT_TAG'):
    version = environ['CI_COMMIT_TAG']
else:
    version = '2.0.0.8-SNAPSHOT' # default to last version of geopackage-python

setup(
    name='geopackage_python',
    version=version,
    package_dir={'scripts': ''},
    # list of packages to export: Note we are excluding anything requiring gdal
    packages=['rgi',
              'rgi.geopackage',
              'rgi.geopackage.common',
              'rgi.geopackage.nsg',
              'rgi.geopackage.nsg.resources',
              'rgi.geopackage.srs',
              'rgi.geopackage.core',
              'rgi.geopackage.tiles',
              'rgi.geopackage.utility',
              'rgi.geopackage.writers',
              'rgi.geopackage.extensions',
              'rgi.geopackage.extensions.metadata',
              'rgi.geopackage.extensions.metadata.metadata_reference',
              'rgi.geopackage.extensions.vector_tiles',
              'rgi.geopackage.extensions.vector_tiles.vector_fields',
              'rgi.geopackage.extensions.vector_tiles.vector_layers',
              'rgi.geopackage.extensions.vector_tiles.vector_styles'
              ],
    url='https://gitlab.com/GitLabRGI/erdc/geopackage-python',
    license=""" The MIT License (MIT)
             
                Copyright (c) 2015 Reinventing Geospatial, Inc.
            
                Permission is hereby granted, free of charge, to any person obtaining a copy
                of this software and associated documentation files (the "Software"), to deal
                in the Software without restriction, including without limitation the rights
                to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                copies of the Software, and to permit persons to whom the Software is
                furnished to do so, subject to the following conditions:
            
                The above copyright notice and this permission notice shall be included in all
                copies or substantial portions of the Software.
            
                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
                SOFTWARE.
            """,
    author='Reinventing Geospatial Inc (RGi), Steven Lander, Jenifer Cochran',
    author_email='developer.publishers@rgi-corp.com',
    description='Python-based tools for creating OGC GeoPackages.',
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    # next two lines needed to test with command line arguments (--exclude-gdal)
    tests_require=["pytest"],
    cmdclass={"pytest": PyTest},
    # include the resource files stated in MANIFEST.in. Required for nsg metadata to work
    include_package_data=True
)
