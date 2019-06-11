# -*- coding: utf-8 -*-

from os import path
from setuptools import find_packages, setup

ROOT_DIR = path.abspath(path.dirname(__file__))

try:
    with open(path.join(ROOT_DIR, "README.md"), "r", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except IOError:
    LONG_DESCRIPTION = ""

# Setup specification
setup(
    name="statnett-api-client",
    version="0.1.3",
    description="Statnett API Client",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Alex Piskun",
    author_email="piskun.aleksey@gmail.com",
    url="https://github.com/viktorsapozhok/statnett-api-client",
    keywords=['Statnett', 'API', 'Nordic power flow', 'Nordic power balance'],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    packages=find_packages("src"),
    install_requires=[
        "requests",
        "pandas>=0.24.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
