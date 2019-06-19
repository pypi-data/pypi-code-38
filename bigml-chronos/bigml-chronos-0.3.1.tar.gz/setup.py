# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import sys
from setuptools import setup

# Get the path to this project
project_path = os.path.dirname(__file__)

# Read the version from bigml.chronos.__version__ without importing
# the package (and thus attempting to import packages it depends on
# that may not be installed yet)
init_py_path = os.path.join(project_path, 'bigml', 'chronos', '__init__.py')
print(open(init_py_path).read())

version = re.search("__version__ = '([^']+)'",
                    open(init_py_path).read()).group(1)

# Concatenate files into the long description
file_contents = []
for file_name in ["readme.md"]:
    path = os.path.join(os.path.dirname(__file__), file_name)
    file_contents.append(open(path).read())
long_description = '\n\n'.join(file_contents)

PYTHON_VERSION = sys.version_info[0:3]
INSTALL_REQUIRES = ["isoweek", "pytz"]

setup(
    name="bigml-chronos",
    description="Utilities for parsing time strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    author="The BigML Team",
    author_email="bigml@bigml.com",
    url="https://bigml.com",
    download_url="https://github.com/bigmlcom/chronos",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    setup_requires = ['nose'],
    install_requires = INSTALL_REQUIRES,
    packages = ['bigml.chronos', 'bigml.chronos.tests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=2.7',
    test_suite='nose.collector',
    use_2to3=True,
)
