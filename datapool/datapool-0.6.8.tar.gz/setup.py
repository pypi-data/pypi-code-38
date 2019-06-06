#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

readme = """EAWAG sensor data warehouse

"""

# !!!! DO NOT FORGET TO UPDATE requirements.txt !!!!!

requirements = [
    "sqlalchemy>=1.2",
    "psycopg2-binary",
    "Click>=7",
    "ruamel.yaml",
    "psutil",
    "watchdog",
    "pandas",
    "prometheus_client",
]

# !!!! DO NOT FORGET TO UPDATE requirements.txt !!!!!


setup(
    name="datapool",
    version="0.6.8",  # no need to update datapool/__init__.py
    description="EAWAG data warehouse",
    long_description=readme,
    author="Uwe Schmitt",
    author_email="uwe.schmitt@id.ethz.ch",
    url="https://github.com/uweschmitt/datapool",
    packages=find_packages(exclude=["tests", "sandbox"]),
    package_dir={"datapool": "datapool"},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords="datapool",
    python_requires='>3.5',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    entry_points="""
        [console_scripts]
        pool=datapool.main:main
    """,
)
