#!/usr/bin/env python
# Setuptools : https://github.com/kennethreitz/setup.py

from setuptools import setup
from setuptools import find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='htpio',
    version='1.1.0.4',
    author='Branimir Georgiev',
    author_email='bgeorgiev@hilscher.com',
    description='Remote GPIO access library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Copyright (c) Hilscher GmbH',
    keywords='raspberry gpio telnet pigpio',
    url="https://bitbucket.org/hilscherdtc/htpio",
    project_urls={
        "Hilscher": "https://www.hilscher.com",
        "Ticket": "https://ticket.hilscher.com/browse/PSTSKVARNA-765",
        "Documentation": "https://kb.hilscher.com/display/EBG/Power+Reset+Automated+Tests"
    },
    install_requires=['pigpio'],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
            'console_scripts': [
                'htpio = htpio.__main__:main',
            ]
    },
    classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: Other/Proprietary License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
        ],
)
