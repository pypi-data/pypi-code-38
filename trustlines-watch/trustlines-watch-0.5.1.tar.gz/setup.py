#!/usr/bin/env python3

from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="trustlines-watch",
    packages=["tlwatch"],
    setup_requires=["setuptools_scm"],
    description="monitor trustlines cluster with riemann",
    long_description=long_description,
    use_scm_version=True,
    install_requires=["requests", "bernhard", "click", "psycopg2>=2.7"],
    url="https://github.com/trustlines-protocol/watch",
    # Author details
    author="Trustlines-Network",
    author_email="contact@brainbot.com",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 2 - Pre-Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points="""
        [console_scripts]
        tl-watch=tlwatch.cli:cli
    """,
)
