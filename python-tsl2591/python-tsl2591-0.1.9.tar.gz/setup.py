#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os, re, io

####################################
# Package meta-data.
####################################
name = 'python-tsl2591'
package = 'python_tsl2591'
description = "Community-coded Python module for TSL2591 sensor converted from Adafruit's TSL2591 library. Use at your own risk."
url = 'http://github.com/kyletaylored/python-tsl2591'
email = 'maxhofb@gmail.com'
author = 'Max Hofbauer'

# What packages are required for this module to be executed?
requirements = ['smbus2>=0.2', ]

setup_requirements = [ ]

test_requirements = [ ]

# What packages are optional?
extras = {
    # 'fancy feature': ['django'],
}
####################################
# End Metadata
####################################

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py.
verstr = "Unknown"
VERSIONFILE = os.path.join(package, "__version__.py")
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

####################################
# Setuptools
####################################
setup(
    author=author,
    author_email=email,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Operating System :: POSIX :: Linux",
    ],
    description=description,
    install_requires=requirements,
    extras_require=extras,
    license="MIT license",
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords=['python_tsl2591', 'tsl2591', 'light sensor', 'adafruit'],
    name=name,
    packages=find_packages(include=['python_tsl2591']),
    setup_requires=setup_requirements,
    url=url,
    version=verstr,
    zip_safe=False,
)
