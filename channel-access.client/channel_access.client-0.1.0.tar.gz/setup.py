import os
import sys
from setuptools import setup, PEP420PackageFinder, Extension



if 'EPICS_BASE' not in os.environ or 'EPICS_HOST_ARCH' not in os.environ:
    print(sys.stderr, 'EPICS_BASE and EPICS_HOST_ARCH must be set')
    sys.exit(-1)

if sys.platform == 'darwin':
    libsrc = 'Darwin'
    compiler = 'clang'
elif sys.platform.startswith('linux'):
    libsrc = 'Linux'
    compiler = 'gcc'

epics_base = os.environ['EPICS_BASE']
epics_host_arch = os.environ['EPICS_HOST_ARCH']
epics_inc = os.path.join(epics_base, 'include')
epics_lib = os.path.join(epics_base, 'lib', epics_host_arch)


cac_path = 'src/channel_access/client/cac'
cac_extension = Extension('channel_access.client.cac',
    language = 'c++',
    sources = list(map(lambda s: os.path.join(cac_path, s), [
        'cac.cpp',
        'pv.cpp',
        'convert.cpp'
    ])),
    include_dirs = [
        cac_path,
        epics_inc,
        os.path.join(epics_inc, 'os', libsrc),
        os.path.join(epics_inc, 'compiler', compiler),
    ],
    library_dirs = [ epics_lib ],
    runtime_library_dirs = [ epics_lib ],
    extra_compile_args = ['-Wall', '-std=c++11'],
    libraries=['Com', 'ca']
)


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = 'channel_access.client',
    description = 'Channel Access client library',
    long_description = long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    author = 'André Althaus',
    author_email = 'andre.althaus@tu-dortmund.de',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering'
    ],
    keywords = 'epics ca channel_access',
    packages = PEP420PackageFinder.find('src'),
    package_dir = { '': 'src' },
    ext_modules = [ cac_extension ],
    python_requires = '>= 3.5',
    setup_requires = [ 'setuptools_scm' ],
    install_requires = [ 'channel_access.common' ],
    extras_require = {
        'dev': [ 'tox', 'sphinx', 'pytest', 'channel_access.server' ],
        'doc': [ 'sphinx' ],
        'test': [ 'pytest', 'channel_access.server' ]
    },
    use_scm_version = True
)
