import os
import re
from setuptools import setup, find_packages

def extract_version(verfile):
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"

    with open(verfile, "rt") as f:
        data = f.read()
        mo = re.search(VSRE, data, re.M)

    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (verfile,))

short_desc = ('A python framework for the ISOTEL Data-acquisition & Metering '
              'Smart Gateway for easy integration with Internet of Things.')

long_desc = ('ISOTEL Data-acquisition & Metering Project offers a complete solution '
             'for wired and wireless communication with sensor & control devices. '
             'IDM Project strives for correct presentation of sensor measurements, '
             'accuracy, precision and easy description of their complex transfer '
             'functions to fulfil requirements of accurate metering and precise '
             'control in control systems.\n'
             'Package provides API to IDM Smart Gateway and  in addition hardware '
             'specific support for: Monodaq-U-X, and Energy Control Modules.\n')

setup(
    name='isotel-idm',
    version=extract_version('isotel/idm/_version.py'),
    url='http://isotel.eu/idm',
    author='Isotel Team',
    author_email='pypi@isotel.eu',
    license='LGPL3.0',
    description=short_desc,
    long_description=long_desc,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Manufacturing',

        'Topic :: Communications',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Terminals',
        'Topic :: Terminals :: Serial',

        'Framework :: Flask',
        'Framework :: IPython',
        'Framework :: Jupyter',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='idm gateway data acquisition metering server scalable sensor network protocols heterogeneous hardware devices DIY',
    packages=find_packages(exclude=['IoT', 'contrib', 'docs', 'tests*', 'notebook-samples', 'examples*', 'isotel/idm/devel']),
    install_requires=[
        'requests>=2.19.1',
        'future>=0.16.0',
        'uncertainties>=3.0.2'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "httpretty>=0.9.5"],
)
