#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='pryce',
      version='0.3',
      python_requires='>=3.6',
      description='Option pricing',
      long_description=open('README.rst').read(),
      author='Soeren Wolfers',
      url='https://github.com/soerenwolfers/pryce',
      author_email='soeren.wolfers@gmail.com',
      packages=find_packages(exclude=['*examples']),
      install_requires=['numpy','scipy','swutil','smolyak']
)
