import os
import glob
import setuptools as setup
from setuptools.extension import Extension
from pkg_resources import get_distribution, DistributionNotFound
import numpy

# Environment Variables
CYTHON = os.getenv('CYTHON', None) not in {None, '0'}   # Generate .c from .pyx with cython
CDEBUG = os.getenv('CDEBUG', None) not in {None, '0'}   # Enable profiling and linetrace in cython files for debugging


def get_dist(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None


def get_version():
    with open('VERSION', 'r') as f:
        version = f.read().splitlines()[0]
    with open('brambox/_version.py', 'w') as f:
        f.write('#\n')
        f.write('# Brambox version: Automatically generated version file\n')
        f.write('# Copyright EAVISE\n')
        f.write('#\n\n')
        f.write(f'__version__ = "{version}')
        if CYTHON and CDEBUG:
            f.write('-debug')
        f.write('"\n')

    return version


def find_packages():
    return ['brambox'] + ['brambox.'+p for p in setup.find_packages('brambox')]


def find_extensions():
    ext = '.pyx' if CYTHON else '.c'
    files = list(glob.glob('brambox/**/*'+ext, recursive=True))
    names = [os.path.splitext(f)[0].replace('/', '.') for f in files]
    if CYTHON and CDEBUG:
        extensions = []
        for n,f in zip(names, files):
            extensions.append(Extension(n, [f], define_macros=[('CYTHON_TRACE', '1'), ('CYTHON_TRACE_NOGIL', '1')]))
    else:
        extensions = [Extension(n, [f]) for n, f in zip(names, files)]

    if CYTHON:
        from Cython.Build import cythonize
        if CDEBUG:
            extensions = cythonize(
                extensions,
                gdb_debug=True,
                compiler_directives={'linetrace': True}
            )
        else:
            extensions = cythonize(extensions)

    return extensions


requirements = [
    'pyyaml',
    'numpy',
    'pandas',
    'scipy',
]
pillow_req = 'pillow-simd' if get_dist('pillow-simd') is not None else 'pillow'
requirements.append(pillow_req)


setup.setup(
    # Basic Information
    name='brambox',
    version=get_version(),
    author='EAVISE',
    description='Basic Recipes for Annotations Munching toolBOX',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://gitlab.com/eavise/brambox',

    # Package data
    install_requires=requirements,
    packages=find_packages(),
    scripts=setup.findall('scripts'),
    test_suite='test',
    include_dirs=[numpy.get_include()],
    ext_modules=find_extensions(),

    # Additional options
    zip_safe=False,
)
