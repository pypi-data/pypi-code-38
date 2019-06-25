#!/usr/bin/env python3
from setuptools import setup, find_packages


def read_requirements(filename):
    return [req.strip() for req in open(filename)]


setup(
    name='arkindex-client',
    version=open('VERSION').read().strip(),
    author='Teklia <contact@teklia.com>',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    package_data={
        '': ['*.rst', 'LICENSE', 'README'],
        'arkindex': ['schema.yml'],
    },
    install_requires=read_requirements('requirements-frozen.txt'),
    python_requires=">=3.6",
    extras_require={
        'test': read_requirements('requirements-tests.txt'),
    },
    license='MIT',
    description="API client for the Arkindex project",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    keywords="api client arkindex",
    url="https://gitlab.com/arkindex/api-client",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Text Processing :: Linguistic",
    ],
)
