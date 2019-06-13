import os
from setuptools import setup, find_packages

try: # for pip >= 10
  from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
  from pip.req import parse_requirements

install_reqs = parse_requirements('requires.txt', session=False)

README="""Python class to integrate rasa.io and another customer database"""

setup(
  name='rasaio.integrations',
  version='0.0.10',
  description=README,
  long_description=README,
  long_description_content_type='text/x-rst',
  classifiers=[
    "Programming Language :: Python :: 3.6"
  ],
  author="rasa.io",
  author_email="chandra.bhushan@rasa.io",
  packages=find_packages(),
  python_requires='>=3.6, <4',
  url="https://bitbucket.org/rasa-io/rasa-integrations.git",
  install_requires=[str(ir.req) for ir in install_reqs],
  include_package_data=True,
  zip_safe=True
)
