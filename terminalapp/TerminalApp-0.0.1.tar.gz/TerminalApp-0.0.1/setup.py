# coding=utf-8
from __future__ import absolute_import, division, print_function

from setuptools import find_packages, setup

setup(
    name="TerminalApp",
    version="0.0.1",
    author="cowboy8625",
    description="To make better looking terminal tools... or games.",
    # packages=find_packages("CommandLineApp"),
    py_modules=[
        "terminalapp"
        # "__init__",
        # "asciiesc",
        # "curser_control",
        # "keyboard",
        # "terminal_size",
        # "vectors",
    ],
    package_dir={"": "src"},
    # entry_points={
    #     'console_scripts': [
    #         'tryme=testsetup.main:main',
    #         ],
    #     }
)
