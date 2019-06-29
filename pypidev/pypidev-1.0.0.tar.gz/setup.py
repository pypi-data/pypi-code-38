import os
import re

from setuptools import find_packages
from setuptools import setup

with open("README.rst") as f:
    readme = f.read()

with open("src/pypidev/__init__.py") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="pypidev",
    version=version,
    url="https://github.com/bassaer/pypidev",
    author="Tsubasa Nakayama",
    author_email="app.nakayama@gmail.com",
    description="A simple pypi sample",
    long_description=readme,
    license="Apache 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    keywords="hello, pypi",
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    entry_points={"console_scripts": ["pypidev = pypidev.cli:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
