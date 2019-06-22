# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = None
exec(open("typetalk/version.py").read())


setup(
    name="typetalk",
    version=__version__,
    description="Typetalk API client",
    url="https://github.com/is2ei/typetalk-py",
    license="MIT"
)
