#!/usr/bin/env python3
# -*-coding:utf-8 -*


from setuptools import setup, find_packages

import irsensors


setup(
	name="irsensors",
	version=irsensors.__version__,
	packages=find_packages(),

	author="Gilles HUBERT",
	author_email="gilles.hubert@isen.yncrea.fr",
	description="This package allows to read datas from an IR sensor set connected by USB.",
	long_description=irsensors.__doc__,

	install_requires=["serial"],

	include_package_data=True,

	url="https://github.com/Gillou100/educat_irsensor/tree/master/irsensors",

	classifiers=[
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7"
    ]
)
