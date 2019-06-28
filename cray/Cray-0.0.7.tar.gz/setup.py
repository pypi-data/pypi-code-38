#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="Cray",
    version="0.0.7",
    description="CLI for interacting with the batch processing system",
    long_description="CLI for interacting with the batch processing system",
    author="Dan Reid",
    author_email="dan@senseye.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Intended Audience :: Developers",
        "Environment :: Console",
    ],
    platforms=["Any"],
    scripts=[],
    provides=[],
    install_requires=["cliff", "boto3"],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": ["cray = cray.commands.main:main"],
        "cray": [
            "submit = cray.commands.submit:Submit",
            "cancel = cray.commands.cancel:Cancel",
            "jobs = cray.commands.jobs:Jobs",
            "tasks = cray.commands.tasks:Tasks",
            "logs = cray.commands.logs:Logs",
            "status = cray.commands.status:Status",
        ],
    },
    zip_safe=False,
)
