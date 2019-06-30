# -*- coding: utf-8 -*-

"""Compile the Cython libraries of Pyslvs."""

from os import listdir
from distutils.core import setup, Extension
from platform import system
from Cython.Distutils import build_ext
import numpy

np_include = numpy.get_include()


sources = []
for place in ["."]:
    for source in listdir(place):
        if source.endswith('.pyx'):
            sources.append(place + source)

macros = [
    ('_hypot', 'hypot'),
]

compile_args = [
    '-O3',
]

if system() == 'Windows':
    # Avoid compile error with CYTHON_USE_PYLONG_INTERNALS.
    # https://github.com/cython/cython/issues/2670#issuecomment-432212671
    macros.append(('MS_WIN64', None))
    # Disable format warning.
    compile_args.append('-Wno-format')
    # Disable NumPy warning.
    macros.append(('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'))

# Original src
ext_modules = []
for source in sources:
    ext_modules.append(Extension(
        # Base name
        source.split('/')[-1].split('.')[0],
        # path + file name
        sources=[source],
        language="c",
        include_dirs=[np_include],
        define_macros=macros,
        extra_compile_args=compile_args,
    ))

setup(ext_modules=ext_modules, cmdclass={'build_ext': build_ext})
