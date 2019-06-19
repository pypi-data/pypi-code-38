#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.io.base']

import os
from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.extension.utils import egrep, find_header, find_library
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost', 'libpng']
boost_modules = ['system', 'filesystem']


def libjpeg_version(header):

  vv = egrep(header, r"#\s*define\s+JPEG_LIB_VERSION_(MINOR|MAJOR)\s+(\d+)")
  if not len(vv): return None

  # we have a match, produce a string version of the version number
  major = int(vv[0].group(2))
  minor = int(vv[1].group(2))
  return '%d.%d' % (major, minor)

def libjpeg_turbo_version(header):

  vv = egrep(header, r"#\s*define\s+LIBJPEG_TURBO_VERSION\s+([\d\.]+)")
  if not len(vv): return None
  return vv[0].group(1) + '-turbo'

class jpeg:

  def __init__ (self, requirement='', only_static=False):
    """
    Searches for libjpeg in stock locations. Allows user to override.

    If the user sets the environment variable BOB_PREFIX_PATH, that prefixes
    the standard path locations.

    Parameters:

    requirement, str
      A string, indicating a version requirement for this library. For example,
      ``'>= 8.2'``.

    only_static, boolean
      A flag, that indicates if we intend to link against the static library
      only. This will trigger our library search to disconsider shared
      libraries when searching.
    """

    self.name = 'libjpeg'
    header = 'jpeglib.h'

    candidates = find_header(header)

    if not candidates:
      raise RuntimeError("could not find %s's `%s' - have you installed %s on this machine?" % (self.name, header, self.name))

    found = False

    if not requirement:
      self.include_directory = os.path.dirname(candidates[0])
      self.version = libjpeg_version(candidates[0])

      # special condition (using libjpeg-turbo instead)
      if self.version is None:
        turbo_candidates = find_header('jconfig.h')
        if turbo_candidates:
          self.version = libjpeg_turbo_version(turbo_candidates[0])

      found = True

    else:

      # requirement is 'operator' 'version'
      operator, required = [k.strip() for k in requirement.split(' ', 1)]

      # now check for user requirements
      for candidate in candidates:
        vv = libjpeg_version(candidate)
        available = LooseVersion(vv)
        if (operator == '<' and available < required) or \
           (operator == '<=' and available <= required) or \
           (operator == '>' and available > required) or \
           (operator == '>=' and available >= required) or \
           (operator == '==' and available == required):
          self.include_directory = os.path.dirname(candidate)
          self.version = vv
          found = True
          break

    if not found:
      raise RuntimeError("could not find the required (%s) version of %s on the file system (looked at: %s)" % (requirement, self.name, ', '.join(candidates)))

    # normalize
    self.include_directory = os.path.normpath(self.include_directory)

    # find library
    prefix = os.path.dirname(os.path.dirname(self.include_directory))
    module = 'jpeg'
    candidates = find_library(module, version=self.version, prefixes=[prefix], only_static=only_static)

    if not candidates:
      raise RuntimeError("cannot find required %s binary module `%s' - make sure `%s' is installed on `%s'" % (self.name, module, self.name, prefix))

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
    return [
        ('HAVE_%s' % self.name.upper(), '1'),
        ]

def libtiff_version(header):

  vv = egrep(header, r"#\s*define\s+TIFFLIB_VERSION_STR\s+\"LIBTIFF,\s+Version\s+([\d\.]+).*")
  if not len(vv): return None
  return vv[0].group(1)

class tiff:

  def __init__ (self, requirement='', only_static=False):
    """
    Searches for libtiff in stock locations. Allows user to override.

    If the user sets the environment variable BOB_PREFIX_PATH, that prefixes
    the standard path locations.

    Parameters:

    requirement, str
      A string, indicating a version requirement for this library. For example,
      ``'>= 8.2'``.

    only_static, boolean
      A flag, that indicates if we intend to link against the static library
      only. This will trigger our library search to disconsider shared
      libraries when searching.
    """

    self.name = 'libtiff'
    header = 'tiff.h'

    candidates = find_header(header)

    if not candidates:
      raise RuntimeError("could not find %s's `%s' - have you installed %s on this machine?" % (self.name, header, self.name))

    found = False

    if not requirement:
      self.include_directory = os.path.dirname(candidates[0])
      directory = os.path.dirname(candidates[0])
      version_header = os.path.join(directory, 'tiffvers.h')
      self.version = libtiff_version(version_header)
      found = True

    else:

      # requirement is 'operator' 'version'
      operator, required = [k.strip() for k in requirement.split(' ', 1)]

      # now check for user requirements
      for candidate in candidates:
        directory = os.path.dirname(candidate)
        version_header = os.path.join(directory, 'tiffvers.h')
        vv = libtiff_version(version_header)
        available = LooseVersion(vv)
        if (operator == '<' and available < required) or \
           (operator == '<=' and available <= required) or \
           (operator == '>' and available > required) or \
           (operator == '>=' and available >= required) or \
           (operator == '==' and available == required):
          self.include_directory = os.path.dirname(candidate)
          self.version = vv
          found = True
          break

    if not found:
      raise RuntimeError("could not find the required (%s) version of %s on the file system (looked at: %s)" % (requirement, self.name, ', '.join(candidates)))

    # normalize
    self.include_directory = os.path.normpath(self.include_directory)

    # find library
    prefix = os.path.dirname(os.path.dirname(self.include_directory))
    module = 'tiff'
    candidates = find_library(module, version=self.version, prefixes=[prefix], only_static=only_static)

    if not candidates:
      raise RuntimeError("cannot find required %s binary module `%s' - make sure `%s' is installed on `%s'" % (self.name, module, self.name, prefix))

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
    return [
        ('HAVE_%s' % self.name.upper(), '1'),
        ]

def libgif_version(header):

  vv = egrep(header, r"#\s*define\s+GIFLIB_(RELEASE|MINOR|MAJOR)\s+(\d+)")
  if not len(vv):
    vv = egrep(header, r"#\s*define\s+GIF_LIB_VERSION\s+\"\s*Version\s+([\d\.]+).*\"")
    if not len(vv): return None

    # old style
    return vv[0].group(1)

  # we have a match, produce a string version of the version number
  major = int(vv[0].group(2))
  minor = int(vv[1].group(2))
  release = int(vv[2].group(2))
  return '%d.%d.%d' % (major, minor, release)

class gif:

  def __init__ (self, requirement='', only_static=False):
    """
    Searches for libgif in stock locations. Allows user to override.

    If the user sets the environment variable BOB_PREFIX_PATH, that prefixes
    the standard path locations.

    Parameters:

    requirement, str
      A string, indicating a version requirement for this library. For example,
      ``'>= 8.2'``.

    only_static, boolean
      A flag, that indicates if we intend to link against the static library
      only. This will trigger our library search to disconsider shared
      libraries when searching.
    """

    self.name = 'giflib'
    header = 'gif_lib.h'

    candidates = find_header(header)

    if not candidates:
      raise RuntimeError("could not find %s's `%s' - have you installed %s on this machine?" % (self.name, header, self.name))

    found = False

    if not requirement:
      self.include_directory = os.path.dirname(candidates[0])
      self.version = libgif_version(candidates[0])
      found = True

    else:

      # requirement is 'operator' 'version'
      operator, required = [k.strip() for k in requirement.split(' ', 1)]

      # now check for user requirements
      for candidate in candidates:
        vv = libgif_version(candidate)
        available = LooseVersion(vv)
        if (operator == '<' and available < required) or \
           (operator == '<=' and available <= required) or \
           (operator == '>' and available > required) or \
           (operator == '>=' and available >= required) or \
           (operator == '==' and available == required):
          self.include_directory = os.path.dirname(candidate)
          self.version = vv
          found = True
          break

    if not found:
      raise RuntimeError("could not find the required (%s) version of %s on the file system (looked at: %s)" % (requirement, self.name, ', '.join(candidates)))

    # normalize
    self.include_directory = os.path.normpath(self.include_directory)

    # find library
    prefix = os.path.dirname(os.path.dirname(self.include_directory))
    module = 'gif'
    candidates = find_library(module, version=self.version, prefixes=[prefix], only_static=only_static)

    if not candidates:
      raise RuntimeError("cannot find required %s binary module `%s' - make sure `%s' is installed on `%s'" % (self.name, module, self.name, prefix))

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
    return [
        ('HAVE_%s' % self.name.upper(), '1'),
        ]

jpeg_pkg = jpeg()
tiff_pkg = tiff()
gif_pkg = gif()

system_include_dirs = [
    jpeg_pkg.include_directory,
    tiff_pkg.include_directory,
    gif_pkg.include_directory,
    ]

library_dirs = [
    jpeg_pkg.library_directory,
    tiff_pkg.library_directory,
    gif_pkg.library_directory,
    ]

libraries = \
    jpeg_pkg.libraries + \
    tiff_pkg.libraries + \
    gif_pkg.libraries

define_macros = \
    jpeg_pkg.macros() + \
    tiff_pkg.macros() + \
    gif_pkg.macros()

setup(

    name='bob.io.image',
    version=version,
    description='Image I/O support for Bob',
    url='http://gitlab.idiap.ch/bob/bob.io.image',
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
      Extension("bob.io.image.version",
        [
          "bob/io/image/version.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
      ),

      Library("bob.io.image.bob_io_image",
        [
          "bob/io/image/cpp/tiff.cpp",
          "bob/io/image/cpp/gif.cpp",
          "bob/io/image/cpp/png.cpp",
          "bob/io/image/cpp/jpeg.cpp",
          "bob/io/image/cpp/bmp.cpp",
          "bob/io/image/cpp/pnmio.cpp",
          "bob/io/image/cpp/netpbm.cpp",
          "bob/io/image/cpp/image.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
      ),

      Extension("bob.io.image._library",
        [
          "bob/io/image/main.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
      ),

      Extension("bob.io.image._test",
        [
          "bob/io/image/test.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
        system_include_dirs = system_include_dirs,
        library_dirs = library_dirs,
        libraries = libraries,
        define_macros = define_macros,
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
      'Environment :: Plugins',
    ],

)
