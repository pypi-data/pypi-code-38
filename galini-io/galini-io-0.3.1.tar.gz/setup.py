# Copyright 2018 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils.cmd import Command
from distutils.spawn import find_executable

project_root = Path(__file__).resolve().parent

about = {}
version_path = project_root / 'galini_io' / '__version__.py'
with version_path.open() as f:
    exec(f.read(), about)

with (project_root / 'README.rst').open() as f:
    readme = f.read()

with (project_root / 'CHANGELOG.rst').open() as f:
    changelog = f.read()


class PyTestCommand(TestCommand):
    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = [
            '--cov', 'galini_io',
            '--cov-report=html',
            '--cov-report=term',
            'tests/',
        ]

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        return sys.exit(errno)


if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
    protoc = os.environ['PROTOC']
else:
    protoc = find_executable('protoc')


def generate_proto(source):
    output = source.replace('.proto', '_pb2.py')

    print('Generating {}...'.format(output))

    if not os.path.exists(source):
        print('Protobuf file {} does not exist.'.format(source), file=sys.stderr)
        sys.exit(-1)

    if protoc is None:
        print('protoc executable not found. Please install it.', file=sys.stderr)
        sys.exit(-1)

    command = [protoc, '-Iproto', '--python_out=galini_io', source]
    if subprocess.call(command) != 0:
        sys.exit(-1)


class GenerateProto(Command):
    description = 'Generate _pb2.py files from .proto definition.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        generate_proto('proto/message.proto')


setup(
    name='galini-io',
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    version=about['__version__'],
    long_description=readme + '\n\n' + changelog,
    packages=find_packages(exclude=['tests']),
    cmdclass={
        'generate_proto': GenerateProto,
        'test': PyTestCommand,
    },
    entry_points={
        'console_scripts': [
            'galini_io_writer=galini_io.scripts.writer:main',
            'galini_io_reader=galini_io.scripts.reader:main',
            'galini_io_fake_solver=galini_io.scripts.fake_solver:main',
        ]
    },
    install_requires=[
        'protobuf>=3.6.1',
        'h5py',
        'networkx>=2.2',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    include_package_data=True,
)
