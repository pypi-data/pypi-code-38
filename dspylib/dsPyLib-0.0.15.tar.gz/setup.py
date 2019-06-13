# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dsPyLib",
    keywords="dsPyLib",
    version="0.0.15",
    author="Dragon Sun",
    author_email="dragonsun7@163.com",
    license="MIT",
    description="A common python library for DS.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dragonsun7/dsPyLib",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "psycopg2-binary",
        "python-dateutil"
    ]
)
