#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='seetaas-beta-helper',
      version='0.1.6',
      platforms='any',
      maintainer_email='seetaas@seetatech.com',
      description='SeeTaaS helper functions',
      packages=find_packages(),
      install_requires=[
          'requests==2.18.4',
          'flask==0.12.2',
          'flask-cors==3.0.8',
          'gunicorn==19.7.1',
      ],
      entry_points={
          "console_scripts": [
              "helper = seetaas_helper.config:write_parameter",
          ],
      },
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
      ])
