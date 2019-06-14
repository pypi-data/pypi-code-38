from __future__ import absolute_import, division, print_function
from setuptools import setup
import pyco_sqlalchemy

description = "Easy ORM for Flask and Django Based on SqlAlchemy.ORM"

try:
    with open("README.md", "r") as fh:
        readme = fh.read()
except:
    readme = description

setup(
    name="pyco_sqlalchemy",
    url="https://github.com/dodoru/pyco-sqlalchemy",
    license="MIT",
    version='1.0.2',
    author="dodoru",
    author_email="dodoru@foxmail.com",
    description=(description),
    long_description=readme,
    long_description_content_type="text/markdown",
    zip_safe=False,
    include_package_data=True,
    packages=["pyco_sqlalchemy"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "sqlalchemy",
        "flask-sqlalchemy",
        "python-dateutil"
    ],
    platforms='any',
)
