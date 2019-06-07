
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.rst')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

setup(
    name='pg_python',
    version=find_version('pg_python', '__init__.py'),
    url='http://github.com/ingloriousb/pg_python',
    license='MIT License',
    author='Gaurav Bhati',
    install_requires=['xlrd',
                      'beautifulsoup4',
                      'psycopg2',
                      'scrapy',
                      'selenium'
                      ],
    author_email='gaurav.hawker@gmail.com',
    description='A Library to communicate with postgres from python',
    #long_description=long_description,
    packages=['pg_python'],
    include_package_data=True,
    platforms='any',
    zip_safe=False,
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ]
)
