# -*- coding: utf-8 -*-

from distutils.core import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

setup(
    name="tztab",
    version="0.0.1",
    py_modules=["tztab"],
    description="",
    author="laixintao",
    author_email="laixintaoo@gmail.com",
    url="",
    entry_points={"console_scripts": ["tztab = tztab:cli"]},
    scripts=["tztab.py"],
    install_requires=["click"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["crontab", "timezone"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
