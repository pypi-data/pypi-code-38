# -*- coding: utf-8 -*-
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='data-analyze',
    version='1.0.2',
    description='data-analyze',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='luchang',
    author_email='chang.lu@rokid.com',
    url='https://markdown.felinae.net',
    keywords='data analyze',
    packages=setuptools.find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Django"
    ))