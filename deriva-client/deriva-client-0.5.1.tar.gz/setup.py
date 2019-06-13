#
# Copyright 2019 University of Southern California
# Distributed under the GNU GPL 3.0 license. See LICENSE for more info.
#

""" Installation script for DERIVA Client Tools
"""
import io
from setuptools import setup
from version import __version__


def get_readme_contents():
    with io.open('README.md') as readme_file:
        return readme_file.read()


url = 'https://github.com/informatics-isi-edu/deriva-client'
author = 'USC Information Sciences Institute, Informatics Systems Research Division'
author_email = 'isrd-support@isi.edu'


setup(
    name='deriva-client',
    description='A Python-based application suite of client software for use with the DERIVA platform.',
    long_description=get_readme_contents(),
    long_description_content_type='text/markdown',
    url=url,
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    version=__version__,
    python_requires='>3.5.2',
    install_requires=[
        # temp pin of urllib3 due to current current awscli requiring urllib3 < 1.25 but also
        # need >=1.23 for http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-20060
        'urllib3==1.24.3',
        'bdbag[boto,globus]==1.5.4',
        'deriva==0.8.4',
        'deriva-qt[PyQt5]==0.8.4',
        'deriva-catalog-manage==0.5.0'
    ],
    license='GNU GPL 3.0',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)


