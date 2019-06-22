#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

from setuptools import setup, find_packages

def get_version(*file_paths):
    """Retrieves the version from quartet_epcis/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("quartet_epcis", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()

setup(
    name='quartet_epcis',
    version=version,
    description="""Defines EPCIS models and XML parsing.""",
    long_description=readme,
    author='SerialLab Corp',
    author_email='slab@serial-lab.com',
    url='https://gitlab.com/serial-lab/quartet_epcis',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    python_requires='~=3.5',
    install_requires=[
        'eparsecis',
        'EPCPyYes',
        'django-model-utils',
        'python-dateutil'
    ],
    license="GPLv3",
    zip_safe=False,
    keywords='seriallab quartet_epcis epcis level-4 quartet',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
