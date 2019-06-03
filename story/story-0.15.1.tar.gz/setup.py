# -*- coding: utf-8 -*-
import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install as _install
from setuptools import find_packages, setup, Command

from story.version import version


class Install(_install):
    """Overwrites the default setup.py installation to error on Python < 3.6."""

    def run(self):
        if sys.version_info < (3, 6):
            sys.exit('story requires Python 3.6+')
        _install.run(self)


class PyTest(Command):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        pass

    def finalize_options(self):
        # Command.finalize_options(self)
        pass

    def run(self):
        import pytest

        errno = pytest.main([])

        sys.exit(errno)


class Format(Command):
    user_options = [('black-args', 'a', 'arguments to pass into black.')]

    def initialize_options(self):
        pass

    def finalize_options(self):
        # Command.finalize_options(self)
        pass

    def run(self):
        os.system('black -S -l 79 .')


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.7',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools',
]

keywords = [
    'storyscript',
    'devops',
    'devtools',
    'microservices',
    'orchestration',
    'serverless',
    'APIs',
    'asyncy',
]

requirements = [
    'asyncio>=3.4.3',
    'click-completion==0.5.1',
    'click-help-colors==0.5',
    'click-spinner==0.1.8',
    'click==7.0',
    'emoji==0.5.0',
    'raven==6.9.0',
    'requests>=2.20.0',
    'storyscript==0.19.0',
    'websockets>=7.0',
    'texttable>=1.4.0',
    'pyyaml>=4.2',
    'pytz>=2018.5',
    'blindspin',
    'appdirs',
    'xerox',
    'semver',
]

test_requirements = ["pytest", "delegator.py"]

# Read the README.md as the long_description.
here = os.path.abspath(os.path.dirname(__file__))
long_description_fname = os.path.join(here, 'README.md')
with io.open(long_description_fname, encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='story',
    version=version,
    description='Storyscript Cloud CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    download_url='https://github.com/storyscript/cli/archive/'
    + version
    + '.zip',
    keywords=' '.join(keywords),
    author='Storyscript',
    author_email='hello@storyscript.io',
    url='https://docs.storyscript.io/cli',
    license='Apache 2',
    packages=find_packages(exclude=['scripts', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=requirements,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    tests_require=test_requirements,
    extras_require={},
    requires_python='>=3.6.0',
    entry_points={
        'console_scripts': ['story=story.main:cli', 'asyncy=story.main:cli']
    },
    cmdclass={'install': Install, 'test': PyTest, 'format': Format},
)
