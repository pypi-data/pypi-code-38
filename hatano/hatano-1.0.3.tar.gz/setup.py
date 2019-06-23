from setuptools import setup, find_packages

import os

with open("README.md") as f:
    long_desc = f.read()

here = os.path.abspath(os.path.dirname(__file__))
info = {}
pkg_name = "hatano"

with open(
        os.path.join(here, pkg_name, "__init__.py")) as f:
    exec(f.read(), None, info)

with open("requirements.txt") as f:
    pkgs = [line.strip() for line in f]

setup(
        name=pkg_name,
        version=info['__version__'],
        description=info['__description__'],
        long_description=long_desc,
        long_description_content_type="text/markdown",
        author=info['__author__'],
        author_email=info['__author_email__'],
        url="https://github.com/tripleko-llc/hatano",
        packages=find_packages(),
        install_requires=pkgs,
        entry_points={
            'console_scripts': [
                'hatano = hatano:handle',
                'htn = hatano:handle'
                ]
            },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        )

