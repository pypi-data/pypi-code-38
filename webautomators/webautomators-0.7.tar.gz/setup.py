# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='webautomators',
      version='0.7',
      url='',
      license='MIT License (MIT)',
      author='Raphael Peleje',
      author_email='rmoreirap@indracompany.com',
      description='Application Interaction Library with Web',
      packages=['webautomators', 'test',],
      install_requires=['selenium', 'requests'],
      zip_safe=True,
      test_suite='test',
      long_description=open('README.md').read())
