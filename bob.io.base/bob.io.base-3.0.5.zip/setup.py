#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.extension.utils import egrep, find_header, find_library
from bob.extension import pkgconfig
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']
boost_modules = ['system', 'filesystem']

def libhdf5_version(header):

  vv = egrep(header, r"#\s*define\s+H5_VERSION\s+\"([\d\.]+)\"")
  if not len(vv): return None
  return vv[0].group(1)

class hdf5:

  def __init__ (self):
    """
    Searches for libhdf5 in stock locations. Allows user to override.

    If the user sets the environment variable BOB_PREFIX_PATH, that prefixes
    the standard path locations.

    """
    import os

    self.name = 'hdf5'

    # try to locate pkg-config on our own first
    try:

      header = 'hdf5.h'

      candidates = find_header(header)

      if not candidates:
        raise RuntimeError("could not find %s's `%s' - have you installed %s on this machine?" % (self.name, header, self.name))

      self.include_directories = [os.path.dirname(candidates[0])]
      directory = os.path.dirname(candidates[0])
      version_header = os.path.join(directory, 'H5pubconf.h')
      self.version = libhdf5_version(version_header)

      # normalize
      self.include_directories = [os.path.normpath(i) for i in self.include_directories]

      # find library
      prefix = os.path.dirname(os.path.dirname(self.include_directories[0]))
      module = 'hdf5'
      candidates = find_library(module, version=self.version, prefixes=[prefix], only_static=False)

      if not candidates:
        raise RuntimeError("cannot find required %s binary module `%s' - make sure libhdf5 is installed on `%s'" % (self.name, module, prefix))

      # libraries
      self.libraries = []
      name, ext = os.path.splitext(os.path.basename(candidates[0]))
      if ext in ['.so', '.a', '.dylib', '.dll']:
        self.libraries.append(name[3:]) #strip 'lib' from the name
      else: #link against the whole thing
        self.libraries.append(':' + os.path.basename(candidates[0]))

      # library path
      self.library_directories = [os.path.dirname(candidates[0])]

    except RuntimeError:
      # now, we try to use pkg-config, which seems to be only available on Debian
      pkg = pkgconfig('hdf5')
      self.include_directories = pkg.include_directories()
      version_header = os.path.join(self.include_directories[0], 'H5pubconf.h')
      self.version = libhdf5_version(version_header)
      self.libraries = pkg.libraries()
      self.library_directories = pkg.library_directories()


  def macros(self):
    return [
        ('HAVE_%s' % self.name.upper(), '1'),
        ]


hdf5_pkg = hdf5()

system_include_dirs = hdf5_pkg.include_directories

library_dirs = hdf5_pkg.library_directories

libraries = hdf5_pkg.libraries

define_macros = hdf5_pkg.macros()


setup(

    name='bob.io.base',
    version=version,
    description='Basic IO for Bob',
    url='http://gitlab.idiap.ch/bob/bob.io.base',
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
      Extension("bob.io.base.version",
        [
          "bob/io/base/version.cpp",
        ],
        define_macros = define_macros,
        system_include_dirs = system_include_dirs,
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Library("bob.io.base.bob_io_base",
        [
          "bob/io/base/cpp/CodecRegistry.cpp",
          "bob/io/base/cpp/CSVFile.cpp",
          "bob/io/base/cpp/File.cpp",
          "bob/io/base/cpp/HDF5ArrayFile.cpp",
          "bob/io/base/cpp/HDF5Attribute.cpp",
          "bob/io/base/cpp/HDF5Dataset.cpp",
          "bob/io/base/cpp/HDF5File.cpp",
          "bob/io/base/cpp/HDF5Group.cpp",
          "bob/io/base/cpp/HDF5Types.cpp",
          "bob/io/base/cpp/HDF5Utils.cpp",
          "bob/io/base/cpp/reorder.cpp",
          "bob/io/base/cpp/T3File.cpp",
          "bob/io/base/cpp/TensorArrayFile.cpp",
          "bob/io/base/cpp/TensorFileHeader.cpp",
          "bob/io/base/cpp/utils.cpp",
          "bob/io/base/cpp/TensorFile.cpp",
          "bob/io/base/cpp/array.cpp",
          "bob/io/base/cpp/array_type.cpp",
          "bob/io/base/cpp/blitz_array.cpp",
        ],
        libraries = libraries,
        library_dirs = library_dirs,
        system_include_dirs = system_include_dirs,
        define_macros = define_macros,
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.io.base._library",
        [
          "bob/io/base/bobskin.cpp",
          "bob/io/base/codec.cpp",
          "bob/io/base/file.cpp",
          "bob/io/base/hdf5.cpp",
          "bob/io/base/main.cpp",
        ],
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
        system_include_dirs = system_include_dirs,
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.io.base._test",
        [
          "bob/io/base/test.cpp",
        ],
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
        system_include_dirs = system_include_dirs,
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
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
