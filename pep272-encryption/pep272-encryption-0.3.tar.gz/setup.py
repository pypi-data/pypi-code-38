"""
Installation script of pep272-encryption.
Usage (pip):
    pip install .
Usage (direct):
    setup.py build  # "Build" + Checkup
    setup.py install  # Installation
"""

import platform
import sys
import traceback

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    sys.stderr.write("Warning: setuptools not found! "
                     "Falling back to raw distutils.\n")
    sys.stderr.write(" -> This may not properly register packages "
                     "within python.\n\n")

# Cython Speedup

try:
    import Cython
except ImportError:
    CYTHON = False
else:
    from Cython.Build import cythonize
    CYTHON = True

CPYTHON = platform.python_implementation() == "CPython"

possible_builds = 1  # C-Ext is optional and may not work

if CPYTHON:
    possible_builds +=1
    if CYTHON:
        possible_builds +=1

with open('pep272_encryption/version.py') as version_file:
    exec(version_file.read())


description='Library for easy creation of PEP-272 cipher classes'

try:
    with open('README.rst') as description_file:
        long_description = description_file.read()
except:
    long_description = description


args = dict(
    name='pep272-encryption',
    version=__version__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    url=__url__,
    platforms='any',

    description=description,
    long_description=long_description,

    packages=['pep272_encryption'],
    classifiers = [
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
)


def cython_setup(**args):
    print("[   ] Configuration: Cythonize")
    nargs = args.copy()
    extensions = [
        Extension(
            "pep272_encryption._fast_xor",
            ["pep272_encryption/_fast_xor.pyx"]
    )]
    nargs["ext_modules"] = cythonize(extensions)
    setup(**nargs)

def cspeed_setup(**args):
    print("[   ] Configuration: Use C-Extension")
    nargs = args.copy()
    extensions = [
        Extension(
            "pep272_encryption._fast_xor",
            ["pep272_encryption/_fast_xor.c"]
    )]
    nargs["ext_modules"] = extensions
    setup(**nargs)

print("Important note:")
print("---------------")
print()
print("This module supports optimization with Cython.")
print()
print("Depending on your software installation (e.g. compiler or Cython), "
      "it may or not work. If Cython is not installed it falls back to a "
      "pre-generated C-file, if no compiler is installed or another 'edition' "
      "like PyPy or Jython is used, the pure-Python-module will be used.")
print("The setup will not fail - it will fall back to the unoptimized "
      "code if using Cython fails and shows each try with a counter.")
print()
print("Even on commands like 'sdist' the build counter will appear, but "
      "can safely be ignored.")
print()
for i in range(possible_builds):
    i += 1
    print("[{0}/{1}] Starting...".format(i, possible_builds))

    if CYTHON and CPYTHON:
        if i == 1:
            try:
                cython_setup(**args)
                break
            except:
                traceback.print_exc()
                print("[{0}/{1}] Failed!...".format(i, possible_builds))
        elif i == 2:
            try:
                cspeed_setup(**args)
                break
            except:
                traceback.print_exc()
                print("[{0}/{1}] Failed!...".format(i, possible_builds))
        else:
            try:
                setup(**args)
                break
            except:
                traceback.print_exc()
                print("[{0}/{1}] Failed!...".format(i, possible_builds))

    elif CPYTHON and not CYTHON:
        if i == 1:
            try:
                cspeed_setup(**args)
                break
            except:
                traceback.print_exc()
                print("[{0}/{1}] Failed!...".format(i, possible_builds))
        else:
            try:
                setup(**args)
                break
            except:
                traceback.print_exc()
                print("[{0}/{1}] Failed!...".format(i, possible_builds))
    else:
        try:
            setup(**args)
            break
        except:
            traceback.print_exc()
            print("[{0}/{1}] Failed!...".format(i, possible_builds))

else:
    print("Setup failed!")
    sys.exit(1)

print("[{0}/{1}] Success! Setup exits.".format(i, possible_builds))
