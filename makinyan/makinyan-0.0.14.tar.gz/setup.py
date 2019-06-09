#!-*-coding:utf-8-*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os
from setuptools import setup,find_packages

#Get Readme
try:
    with open( 'README.rst' ) as f:
        readme = f.read()
except IOError:
    readme = ''


def _get_requirements( filename ):
    """
    Get all information of pre install required modules
    """
    return open(filename).read().splitlines()


pwd = os.path.dirname(os.path.abspath(__file__))
version = '0.0.14'

setup(
    name='makinyan',
    version=version,
    py_modules=['makinyan'],
    url='https://github.com/Shochan024/makinyan',
    author='shochan024',
    author_email='jadetech0024@gmail.com',
    maintainer='shochan024',
    maintainer_email='jadetech0024@gmail.com',
    description='Python Data Analitics Tool',
    long_description="readme",
    packages=find_packages(),
    install_requires=_get_requirements('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        pkgdep = pypipkg.scripts.command:main
    """,
)
