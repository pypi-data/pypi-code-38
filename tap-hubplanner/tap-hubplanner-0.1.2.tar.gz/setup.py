#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-hubplanner",
    version="0.1.2",
    description="Singer.io tap for extracting data from the Hub Planner REST API",
    author="Rangle.io",
    url="https://github.com/rangle/tap-hubplanner",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_hubplanner"],
    install_requires=[
        "singer-python==5.5.0",
        "requests==2.21.0",
        "backoff==1.3.2",
        "ratelimit==2.2.1"
    ],
    extras_require={
        'dev': [
            'pylint',
            'autopep8',
            'rope'
        ]
    },
    entry_points="""
    [console_scripts]
    tap-hubplanner=tap_hubplanner:main
    """,
    packages=["tap_hubplanner"],
    package_data = {
        "schemas": ["tap_hubplanner/schemas/*.json"]
    },
    include_package_data=True,
)
