# coding: utf-8

import os
import sys
import logging
from setuptools.command.test import test as TestCommand

logging.basicConfig()
_logger = logging.getLogger(__name__)  # pylint: disable=C0103

if os.environ.get('USER', '') == 'vagrant':
    del os.link

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


readme = open('README.md').read()
requirements = open('requirements.txt').readlines()
test_requirements = open('test-requirements.txt').readlines()

setup(
    name='deployv',
    version='0.9.130',
    description='Base for all clases and scripts in VauxooTools',
    long_description=readme,
    author='Tulio Ruiz',
    author_email='tulio@vauxoo.com',
    url='https://github.com/vauxoo/deployv',
    download_url='https://github.com/vauxoo/deployv',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='vauxootools deployv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    tests_require=test_requirements,
    cmdclass={
        'test': PyTest
    },
    py_modules=['deployv'],
    entry_points='''
        [console_scripts]
        deployvcmd=deployv.commands.deployvcmd:cli
        workerv=deployv.commands.workerv:run
    ''',
    scripts=[]
)
