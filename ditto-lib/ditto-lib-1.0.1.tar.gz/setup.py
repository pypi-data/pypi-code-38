from setuptools import setup, find_packages

setup(name = 'ditto-lib',
version = "1.0.1",
description = 'Data analysis tools',
url = 'https://github.com/hgromer/ditto',
author = 'Hernan Gelaf-Romer',
author_email = 'nanug33@gmail.com',
license = 'MIT',
packages = find_packages(),
install_requires = [
    "colorlogging",
    "ordered-set"
    ],
zip_safe = False)