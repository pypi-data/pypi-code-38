# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

long_description = ""
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="typetalk",
    version="0.0.25",
    packages=['typetalk'],
    description="Typetalk API client",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Issei Horie',
    url="https://github.com/is2ei/typetalk-py",
    license="MIT"
)
