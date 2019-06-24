#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='insightconnect_integrations_plugin_spec_tooling',
      version='1.0.0',
      description='Plugin spec parser tooling for InsightConnect integrations',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Rapid7 Integrations Alliance',
      author_email='integrationsalliance@rapid7.com',
      url='https://github.com/rapid7/icon-integrations-plugin-spec',
      packages=find_packages(),
      install_requires=[
          'ruamel.yaml==0.15.81',
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
      ],
      license="MIT"
      )
