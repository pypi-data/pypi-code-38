# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

version = "0.0.1"

with open('README.md') as f:
    readme = f.read()

setup(
    name="botouk",
    version=version,
    url='https://github.com/ukwksk/botouk',
    packages=[package for package in find_packages()
              if package.startswith('botouk')],
    description="Boto Wrapper",
    long_description=readme,
    keywords="AWS Boto3",
    author='ukwksk',
    author_email='pylibs@ukwksk.co',
    maintainer='ukwksk',
    maintainer_email='pylibs@ukwksk.co',
    python_requires='>=3.6',
    install_requires=[
        'boto3',
    ],
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)
