"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname

from setuptools import find_packages, setup

import dli

this_dir = abspath(dirname(__file__))
# with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
#     long_description = file.read()

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='dli',
    version=dli.__version__,
    description='Data Lake command line Interface.',
    # long_description=long_description,
    # url='https://git.mdevlab.com/data-lake/data-lake-sdk',
    author='IHS Markit Data Lake Team',
    author_email='DataLake-Support_L1@ihsmarkit.com',
    license='MOZ-2',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli, datalake, data, lake',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=requirements,
    setup_requires=['urllib3'],
    entry_points={
        'console_scripts': [
            'dli=dli.dli:main',
        ],
    },
)
