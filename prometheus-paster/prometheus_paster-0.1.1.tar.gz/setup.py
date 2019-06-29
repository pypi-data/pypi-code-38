#!/usr/bin/env python
# coding: UTF-8
from setuptools import setup, find_packages

setup(
    name='prometheus_paster',
    version='0.1.1',
    author="Kawai Hiroaki",
    author_email="hiroaki.kawai@gmail.com",
    description="prometheus_client and pastedeploy glue",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hkwi/python-prometheus-paster",
    packages=find_packages(),
    py_modules=["prometheus_paster"],
    entry_points={
        'paste.app_factory':[
          'main=prometheus_paster:factory'
        ],
        'paste.filter_factory':[
          'filter=prometheus_paster:filter_factory',
        ],
    },
    install_requires=[
        'prometheus_client'
    ],
)
