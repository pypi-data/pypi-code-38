# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amarettopy",
    version="0.0.5",
    author="SR",
    author_email="sr-dev@smartrobotics.jp",
    description="python API for Buildit Actuator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['crc8','numpy','pyserial', 'matplotlib', 'numpy', 'pyyaml'],
    url="https://github.com/Smartrobotics/AmarettoPy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'amarettopy': ['gui/imgs/*.gif', 'gui/config/*.yml'] },
    entry_points={
        'console_scripts':[
            'amrtctl = amarettopy.cli.amrtctl:main',
        ],
        'gui_scripts':[
            'amrtctl-gui = amarettopy.gui.amrtctl:main',
        ],
    },
)
