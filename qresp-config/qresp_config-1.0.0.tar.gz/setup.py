# -*- coding: utf-8 -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup,find_packages
 
 

 
setup(
    name = "qresp_config",
    entry_points = {
        "console_scripts": ['qresp_config = qresp_config.qresp_config:main']
        },
	version='1.0.0',
    description = "Python command line application to configure qresp.",
    author = "Aditya Tanikanti, Marco Govoni",
	author_email='datadev@lists.uchicago.edu',
	license='MIT',
	python_requires='>=3.0',
	packages=find_packages(),
	install_requires=[
          'configparser'
    ],
	include_package_data = True
)
