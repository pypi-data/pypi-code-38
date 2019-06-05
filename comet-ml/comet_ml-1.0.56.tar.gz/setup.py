# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import setuptools

setuptools.setup(
    name="comet_ml",
    packages=["comet_ml", "comet_ml.scripts"],
    package_data={"comet_ml": ["schemas/*.json"]},
    version="1.0.56",
    url="https://www.comet.ml",
    author="Comet ML Inc.",
    author_email="mail@comet.ml",
    description="Supercharging Machine Learning",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    install_requires=[
        "websocket-client>=0.55.0",
        "requests>=2.18.4",
        "six",
        "wurlitzer>=1.0.2",
        "netifaces>=0.10.7",
        "nvidia-ml-py3>=7.352.0",
        "comet-git-pure>=0.19.11",
        "everett==0.9 ; python_version<'3.0'",
        "everett[ini]>=1.0.1 ; python_version>='3.0'",
        "jsonschema>=2.6.0",
    ],
    test_requires=["websocket-server", "pytest", "responses", "IPython"],
    entry_points={
        "console_scripts": ["comet-upload = comet_ml.scripts.comet_upload:main"]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
