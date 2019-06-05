# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(ROOT_DIR, "README.md"), "r", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except IOError:
    LONG_DESCRIPTION = ""

setup(
    name="db-commuter",
    version="0.1.3",
    description="Database communication manager",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Alex Piskun",
    author_email="piskun.aleksey@gmail.com",
    url="https://github.com/viktorsapozhok/db-commuter",
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    packages=find_packages("src"),
    install_requires=[
        "pandas>=0.24.0",
        "sqlalchemy>=1.3.3",
        "psycopg2-binary>=2.7.7"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
