import re
import os
from setuptools import setup, Extension
from codecs import open
from os import path

version_file = open("tsfm/_version.py", "r").read()
version_match = re.match(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file)
if (version_match):
    version = version_match.group(1)
else:
    raise RuntimeError("Unable to find version string in _version.py")

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
#bpexact_ext = Extension('bplogofun.exact', ['src/exact.c'])

setup(name = "tsfm",
      setup_requires=['cython','pytest-runner'],
      tests_require=['pytest'],
      install_requires=['cython', 'scipy', 'pandas', 'patsy', 'mpmath','statsmodels', 'numpy'],
      python_requires='~=3.5',
      packages = ["tsfm"],
      package_data={'tsfm': ['eps/Template.eps', 'eps/inverse_template.eps']},
      entry_points = {
          "console_scripts": ['tsfm = tsfm.tsfm:main']},
      version = version,
      author="Travis J. Lawrence and David H. Ardell",
      author_email="tlawrence3@ucmerced.edu",
      description = "tRNA structure function mapper",
      long_description=long_description,
      license='LGPLv3',
      url = "https://github.com/tlawrence3/tsfm",
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Natural Language :: English',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Topic :: Scientific/Engineering :: Bio-Informatics'],
      ext_modules=[Extension('tsfm.exact',['src/exact.c'])],)
