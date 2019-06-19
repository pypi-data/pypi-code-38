import sys
from distutils.cmd import Command
from itertools import chain
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

production_packages = ('putput',)
support_packages = ('samples', 'tests')


class _BaseCommand(Command):
    user_options = []  # type: ignore

    root_dir = Path(__file__).parent

    @property
    def test_paths(self):
        for module in chain(production_packages, support_packages):
            yield str(self.root_dir / module)
        yield __file__

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _run(self, path):
        raise NotImplementedError

    def run(self):
        for test_path in self.test_paths:
            self._run(test_path)


class Pylint(_BaseCommand):
    description = 'Run pylint on source files'

    def _run(self, path):
        try:
            from pylint.lint import Run
        except ImportError:
            print('Unable to import pylint', file=sys.stderr)
        else:
            args = [path]
            rcfile = self.root_dir / '.pylintrc'
            if rcfile.is_file():
                args.append('--rcfile={}'.format(rcfile))
            error = Run(args, do_exit=False).linter.msg_status
            if error:
                sys.exit(error)


class Mypy(_BaseCommand):
    description = 'Run mypy on source files'

    def _run(self, path):
        try:
            from mypy.main import main
        except ImportError:
            print('Unable to import mypy', file=sys.stderr)
        else:
            args = [path]
            rcfile = self.root_dir / '.mypy.ini'
            if rcfile.is_file():
                args.append('--config-file={}'.format(rcfile))
            main(None, args)

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read().strip()

with open('version.txt', 'r', encoding='utf-8') as fh:
    version = fh.read().strip()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = [line.strip() for line in fh]

with open('requirements-dev.txt', 'r', encoding='utf-8') as fh:
    requirements_dev = [line.strip() for line in fh]

if sys.version_info[:2] <= (3, 4):
    requirements.append('typing')

setup(
    name='putput',
    version=version,
    author='Michael Perel',
    author_email='michaelsethperel@gmail.com',
    description='Generate labeled data for conversational AI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/michaelperel/putput',
    packages=find_packages(exclude=support_packages + tuple(mod + '.*' for mod in support_packages)),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5.*',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev,
    },
    cmdclass={
        'pylint': Pylint,
        'mypy': Mypy
    },
)
