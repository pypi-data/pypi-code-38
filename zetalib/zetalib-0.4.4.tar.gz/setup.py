## -*- encoding: utf-8 -*-
import sys
import subprocess

from setuptools import setup
from codecs import open # To open the README file with proper encoding
from setuptools.command.test import test as TestCommand # for tests
from setuptools.extension import Extension
from Cython.Distutils import build_ext

# Get information from separate files (README, VERSION)
def readfile(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

# For the tests
class SageTest(TestCommand):
    def run_tests(self):
        subprocess.check_call(["sage", "-t", "--force-lib", "docs/source", "zetalib"])

# Hack to make sure `make build` is called before bdist_wheel.
try:
    from wheel.bdist_wheel import bdist_wheel
    class MakeBuild(bdist_wheel):
        def run(self):
            subprocess.check_call(["make", "build"])
            bdist_wheel.run(self)
except ImportError:
    # TODO: Change to logging.warn(...) and let MakeBuild = None
    sys.exit("The wheel package is needed for bdist_wheel to work. "
             "It can be installed by running `sage -pip install wheel`")

setup(
    name = "zetalib",
    version = readfile("VERSION").strip(), # the VERSION file is shared with the documentation
    description='computing zeta functions of groups, algebras, and modules',
    long_description = readfile("README.rst"), # get the long description from the README
    url='https://gitlab.com/mathzeta2/zetalib',
    author='Tobias Rossmann, Tomer Bauer',
    license='GPLv3+', # This should be consistent with the LICENSE file
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Scientific/Engineering :: Mathematics',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
    ], # classifiers list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords = "SageMath packaging",
    packages = ['zetalib'],
    package_data = {'zetalib': ['addmany.pyx',
                                'crunch.*',
                                'p-adic-examples.json',
                                ]},
    cmdclass = {
        'test': SageTest, # adding a special setup command for tests
        'bdist_wheel': MakeBuild,
        'build_ext': build_ext, # For cython files
    },
    ext_modules = [Extension("zetalib.addmany", ["zetalib/addmany.pyx"], include_dirs=['zetalib/'])],
)
