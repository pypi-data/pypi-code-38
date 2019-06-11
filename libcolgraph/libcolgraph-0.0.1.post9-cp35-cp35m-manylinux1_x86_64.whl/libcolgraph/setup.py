#!/usr/bin/env python3
# setup.py

import setuptools
from distutils.core import setup, Extension
from distutils.command.build import build
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()


colgraph_module = Extension('_libcolgraph', sources=['libcolgraph.i',
                                                     'Graph.cpp',
                                                     'Vertex.cpp'],
                             swig_opts=['-c++'],
                             extra_compile_args=['-std=gnu++11'])

setup(name='libcolgraph',
      ext_modules=[colgraph_module],
      cmdclass = {'build_py': build_py},
      py_modules=['libcolgraph'])
