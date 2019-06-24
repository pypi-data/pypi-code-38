#!/usr/bin/env python3
import setuptools
import sys

from oris import __version__, __title__, __url__, __author__, __email__, \
    __license__, __description__


if sys.version_info < (3, 7):
    sys.exit('Python < 3.7 is not supported')

setuptools.setup(
    version=__version__,
    name=__title__,
    description=__description__,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.7",
    install_requires=['scipy', 'numpy', 'matplotlib', 'numba',
                      'antlr4-python3-runtime'],
    include_package_data=True,       # reads the rest from MANIFEST.in
    zip_safe=False,
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)
