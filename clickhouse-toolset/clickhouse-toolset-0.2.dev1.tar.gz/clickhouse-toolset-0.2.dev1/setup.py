import glob
import os
import subprocess
import sys
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


NAME = 'clickhouse-toolset'
VERSION = '0.2.dev1'

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CLICKHOUSE_PATH = os.path.join(ROOT_DIR, 'ClickHouse')
CLICKHOUSE_BUILD_PATH = os.path.join(CLICKHOUSE_PATH, 'build')

class ClickHouseParsersBuildExt(build_ext):
    def run(self):
        cmake_cmd = os.environ.get('CMAKE_BIN', 'cmake')
        try:
            out = subprocess.check_output([cmake_cmd, '--version'])
        except OSError:
            raise RuntimeError(
                'CMake must be installed to build the following extensions: ' +
                ', '.join(e.name for e in self.extensions))

        if not os.path.exists(os.path.join(CLICKHOUSE_PATH, 'CMakeLists.txt')):
            raise RuntimeError('Git submodules are not initialized. Run: `git submodule update --init --recursive`.')

        if not os.path.exists(CLICKHOUSE_BUILD_PATH):
            os.makedirs(CLICKHOUSE_BUILD_PATH)

        cmake_args = [
            '-DUSE_STATIC_LIBRARIES=TRUE',
            '-DMAKE_STATIC_LIBRARIES=TRUE',
            '-DENABLE_JEMALLOC=FALSE',
            '-DUSE_JEMALLOC=FALSE',
            '-DENABLE_TESTS=FALSE',
            '-DCMAKE_CXX_FLAGS="-fPIC"',
            '-DCMAKE_BUILD_TYPE=Release',
        ]
        subprocess.check_call([cmake_cmd, CLICKHOUSE_PATH] + cmake_args,
                              cwd=CLICKHOUSE_BUILD_PATH)

        build_args = [
            '--config', 'Release',
            '--target', 'dbms/src/Parsers/libclickhouse_parsers.a',
        ]
        subprocess.check_call([cmake_cmd, '--build', CLICKHOUSE_BUILD_PATH] + build_args)


class BuildExtCommand(build_ext):
    def run(self):
        self.run_command('clickhouse_parsers')
        build_ext.run(self)


class BuildExtFromWheel(build_ext):
    def run(self):
        wheel_target_name = '-'.join([x.replace('-', '_') for x in [
            NAME,
            VERSION,
            f'cp3{sys.version_info[1]}',
            f'cp3{sys.version_info[1]}m',  # cpython + WITH_PYMALLOC
            self.plat_name,
        ]])
        wheel_target_name += '.whl'
        wheel_path = os.path.join(ROOT_DIR, 'dist', wheel_target_name)
        subprocess.check_call(['pip', 'install', wheel_path])


include_dirs = [f'{CLICKHOUSE_PATH}/{rel_path}' for rel_path in [
    'dbms/src',
    'contrib/poco/Foundation/include',
    'libs/libcommon/include',
]]
LIBRARIES_WITH_PATHS = [
    ('clickhouse_parsers', 'dbms/src/Parsers'),
    ('clickhouse_common_io', 'dbms'),
    ('PocoNet', 'contrib/poco/Net'),
    ('PocoFoundation', 'contrib/poco/Foundation'),
    ('double-conversion', 'contrib/double-conversion'),
    ('common', 'libs/libcommon'),
]
library_dirs = [os.path.join(CLICKHOUSE_BUILD_PATH, p) for (_, p) in LIBRARIES_WITH_PATHS]
libraries = [l for (l, _) in LIBRARIES_WITH_PATHS]


chquery = Extension(
    'chtoolset._query',
    sources=['src/query.cpp'],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_compile_args=['-std=c++17',]
)


data_files = []
if 'pip' in __file__:
    build_ext_class = BuildExtFromWheel
else:
    build_ext_class = BuildExtCommand
    if 'bdist_wheel' not in sys.argv:
        data_files.append(('dist', glob.glob(f'dist/{NAME.replace("-", "_")}-{VERSION}-*.whl')))


setup(
    name=NAME,
    version=VERSION,
    url='https://gitlab.com/tinybird/clickhouse-toolset',
    author='Raul Ochoa',
    author_email='raul@tinybird.co',
    packages=find_packages(),
    package_dir={'':'src'},
    data_files=data_files,
    install_requires=[
        'toposort==1.5',
    ],
    extras_require={
        'test': [
            'pytest',
        ]
    },
    cmdclass={
        'clickhouse_parsers': ClickHouseParsersBuildExt,
        'build_ext': build_ext_class,
    },
    ext_modules=[chquery]
)
