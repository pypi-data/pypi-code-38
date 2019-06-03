from __future__ import absolute_import, print_function
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from numpy.distutils.misc_util import get_numpy_include_dirs
from os import path


class build_ext_openmp(build_ext):
    # https://www.openmp.org/resources/openmp-compilers-tools/
    # python setup.py build_ext --help-compiler
    openmp_compile_args = {
        'msvc':  ['/openmp'],
        'intel': ['-qopenmp'],
        '*':     ['-fopenmp']
    }
    openmp_link_args = openmp_compile_args # ?

    def build_extension(self, ext):
        compiler = self.compiler.compiler_type.lower()
        if compiler.startswith('intel'):
            compiler = 'intel'
        if compiler not in self.openmp_compile_args:
            compiler = '*'

        _extra_compile_args = list(ext.extra_compile_args)
        _extra_link_args    = list(ext.extra_link_args)
        try:
            ext.extra_compile_args += self.openmp_compile_args[compiler]
            ext.extra_link_args    += self.openmp_link_args[compiler]
            super(build_ext_openmp, self).build_extension(ext)
        except:
            print('compiling with OpenMP support failed, re-trying without')
            ext.extra_compile_args = _extra_compile_args
            ext.extra_link_args    = _extra_link_args
            super(build_ext_openmp, self).build_extension(ext)


_dir = path.abspath(path.dirname(__file__))

with open(path.join(_dir,'stardist','version.py')) as f:
    exec(f.read())

with open(path.join(_dir,'README.md')) as f:
    long_description = f.read()


setup(
    name='stardist',
    version=__version__,
    description='StarDist',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mpicbg-csbd/stardist',
    author='Uwe Schmidt, Martin Weigert',
    author_email='uschmidt@mpi-cbg.de, mweigert@mpi-cbg.de',
    license='BSD 3-Clause License',
    packages=find_packages(),
    python_requires='>=3.5',

    cmdclass={'build_ext': build_ext_openmp},
    ext_modules=[
        Extension(
            'stardist.lib.stardist',
            sources=['stardist/lib/stardist.cpp','stardist/lib/clipper.cpp'],
            include_dirs=get_numpy_include_dirs(),
        )
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    install_requires=[
        'csbdeep>=0.3.0',
        'scikit-image',
    ],
)