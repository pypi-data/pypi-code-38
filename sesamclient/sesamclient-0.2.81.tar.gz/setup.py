# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import os

from setuptools import setup, find_packages

requires = [
    "idna",
    "appdirs",
    "ijson",
    "python-dateutil",
    "pyyaml",
    "requests",
    "nose",
    "requests_oauthlib",
    "oauthlib",
]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()

with open(os.path.join(here, "sesamclient", 'VERSION.txt')) as f:
    VERSION = f.read().strip()

setup(name='sesamclient',
      version=VERSION,
      description='sesamapi client',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
      ],
      author='Sesam',
      url='http://sesam.io',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      setup_requires=['pip'],
      test_suite="nose.collector",
      install_requires=requires,
      entry_points={
          'console_scripts': [
               'sesam=sesamclient.main.main:main',
          ],
      })
