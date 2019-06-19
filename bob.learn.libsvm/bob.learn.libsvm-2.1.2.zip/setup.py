#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.extension.utils import egrep, find_header, find_library
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']
boost_modules = ['system', 'filesystem']

# process libsvm requirement
import os
from distutils.version import LooseVersion

def libsvm_version(svm_h):

  matches = egrep(svm_h, r"#\s*define\s+LIBSVM_VERSION\s+(\d+)")
  if not len(matches): return None

  # we have a match, produce a string version of the version number
  version_int = int(matches[0].group(1))
  version_tuple = (version_int // 100, version_int % 100)
  return '.'.join([str(k) for k in version_tuple])

class libsvm:
  """A class for capturing configuration information from libsvm

  Example usage:

  .. doctest::
     :options: +NORMALIZE_WHITESPACE +ELLIPSIS

     >>> from bob.learn.libsvm import libsvm
     >>> l = libsvm('>= 3.12')
     >>> l.include_directory
     '...'
     >>> l.version
     '...'
     >>> l.library_directory
     '...'
     >>> l.libraries
     [...]

  """

  def __init__ (self):
    """
    Searches for libsvm in stock locations.

    If the user sets the environment variable BOB_PREFIX_PATH, that prefixes
    the standard path locations.
    """

    candidates = find_header('svm.h', subpaths=['', 'libsvm', 'libsvm-*/libsvm'])

    if not candidates:
      raise RuntimeError("could not find libsvm's `svm.h' - have you installed libsvm on this machine?")

    self.include_directory = os.path.dirname(candidates[0])
    self.version = libsvm_version(candidates[0])

    # normalize
    self.include_directory = os.path.normpath(self.include_directory)

    # find library
    prefix = os.path.dirname(os.path.dirname(self.include_directory))
    module = 'svm'
    candidates = find_library(module, version=self.version,
            prefixes=[prefix], only_static=False)

    if not candidates:
      raise RuntimeError("cannot find required libsvm binary module `%s' - make sure libsvm is installed on `%s'" % (module, prefix))

    # libraries
    self.libraries = []
    name, ext = os.path.splitext(os.path.basename(candidates[0]))
    if ext in ['.so', '.a', '.dylib', '.dll']:
      self.libraries.append(name[3:]) #strip 'lib' from the name
    else: #link against the whole thing
      self.libraries.append(':' + os.path.basename(candidates[0]))

    # library path
    self.library_directory = os.path.dirname(candidates[0])

  def macros(self):
    """Returns package availability and version number macros

    This method returns a python list with 2 macros indicating package
    availability and a version number, using standard GNU compatible names.
    Example:

    .. doctest::
       :options: +NORMALIZE_WHITESPACE +ELLIPSIS

       >>> from bob.learn.libsvm import libsvm
       >>> pkg = libsvm()
       >>> pkg.macros()
       [('HAVE_LIBSVM', '1')]

    """
    return [('HAVE_LIBSVM', '1')]

pkg = libsvm()
system_include_dirs = [pkg.include_directory]
library_dirs = [pkg.library_directory]
libraries = pkg.libraries
define_macros = pkg.macros()

setup(

    name='bob.learn.libsvm',
    version=version,
    description='Python bindings to LIBSVM for Bob',
    url='http://gitlab.idiap.ch/bob/bob.learn.libsvm',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,



    ext_modules = [
      Extension("bob.learn.libsvm.version",
        [
          "bob/learn/libsvm/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        define_macros = define_macros,
        library_dirs = library_dirs,
        libraries = libraries,
      ),

      Library("bob.learn.libsvm.bob_learn_libsvm",
        [
          "bob/learn/libsvm/cpp/file.cpp",
          "bob/learn/libsvm/cpp/machine.cpp",
          "bob/learn/libsvm/cpp/trainer.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        define_macros = define_macros,
        library_dirs = library_dirs,
        libraries = libraries,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.learn.libsvm._library",
        [
          "bob/learn/libsvm/utils.cpp",
          "bob/learn/libsvm/file.cpp",
          "bob/learn/libsvm/machine.cpp",
          "bob/learn/libsvm/trainer.cpp",
          "bob/learn/libsvm/main.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        define_macros = define_macros,
        library_dirs = library_dirs,
        libraries = libraries,
        packages = packages,
        boost_modules = boost_modules,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    entry_points={
      'console_scripts': [
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
