import sys

from setuptools import setup

import versioneer

DISTNAME = 'opat'
DESCRIPTION = "opat is a Python library for evaluatoin of financial portfolios"
LONG_DESCRIPTION = """opat is a Python library for evaluatoin of financial
portfolios. opat standands for Open Portfolio Analysis Tool.
"""
MAINTAINER = 'Shawn Lin'
MAINTAINER_EMAIL = 'shawnlin.xl@gmail.com'
AUTHOR = 'Shawn Lin'
AUTHOR_EMAIL = 'shawnlin.xl@gmail.com'
URL = "https://github.com/shawnlinxl/opat"
LICENSE = "Apache License, Version 2.0"
VERSION = "0.0.2"

classifiers = ['Development Status :: 1 - Planning',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.7',
               'License :: OSI Approved :: Apache Software License',
               'Intended Audience :: Science/Research',
               'Topic :: Scientific/Engineering',
               'Topic :: Scientific/Engineering :: Mathematics',
               'Operating System :: OS Independent']

if (sys.version_info.major, sys.version_info.minor) >= (3, 3):
    support_ipython_6 = True
else:
    support_ipython_6 = False

install_reqs = [
    'numpy>=1.11.1',
    'pandas>=0.18.1',
]

test_reqs = []

if __name__ == "__main__":
    setup(
        name=DISTNAME,
        cmdclass=versioneer.get_cmdclass(),
        version=versioneer.get_version(),
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        long_description=LONG_DESCRIPTION,
        packages=['opat', 'opat.tests'],
        classifiers=classifiers,
        install_requires=install_reqs,
        tests_require=test_reqs,
        test_suite='nose.collector',
    )
