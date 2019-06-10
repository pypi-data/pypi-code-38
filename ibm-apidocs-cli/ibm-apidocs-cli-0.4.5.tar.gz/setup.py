#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys

__version__ = '0.4.5'

# Convert README.md to README.rst for pypi
try:
    from pypandoc import convert_file

    def read_md(f):
        return convert_file(f, 'rst')

    # read_md = lambda f: convert(f, 'rst')
except:
    print('warning: pypandoc module not found, '
          'could not convert Markdown to RST')

    def read_md(f):
        return open(f, 'rb').read().decode(encoding='utf-8')

if sys.argv[-1] == 'publish':
    # test server
    os.system('python setup.py register -r pypitest')
    os.system('python setup.py sdist upload -r pypitest')

    # production server
    os.system('python setup.py register -r pypi')
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'test']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(name='ibm-apidocs-cli',
      version=__version__,
      description='CLI library to automate the API Reference generation',
      license='MIT',
      install_requires=[
          'requests>=2.0, <3.0',
          'outdated>=0.2.0',
          'lxml==4.3.1',
          'PyYAML==3.13'],
      tests_require=['responses', 'pytest', 'python_dotenv', 'pytest-rerunfailures', 'tox'],
      cmdclass={'test': PyTest},
      entry_points={'console_scripts':['ibm-apidocs-cli=ibm_apidocs_cli.main:main']},
      author='IBM Corp',
      author_email='germanatt@us.ibm.com',
      long_description=read_md('README.md'),
      url='https://cloud.ibm.com/apidocs',
      packages=['ibm_apidocs_cli'],
      include_package_data=True,
      keywords='api-reference,  ibm-watson, ibm-cloud',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Libraries :: Application '
          'Frameworks',
      ],
      zip_safe=True
     )
