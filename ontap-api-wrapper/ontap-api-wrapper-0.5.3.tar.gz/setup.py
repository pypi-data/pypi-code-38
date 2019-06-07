#!/usr/bin/env python

from setuptools import setup

setup(name='ontap-api-wrapper',
      version='0.5.3',
      description='Python wrapper for NetApp Manageability SDK',
      author='Andrew Leonard',
      author_email='andy.leonard@sbri.org',
      maintainer='Jiri Machalek',
      maintainer_email='machalekj@gmail.com',
      license='Apache License',
      py_modules=['Ontap'],
      packages=['netapp'],
      install_requires=['six'],
      url='https://github.com/machalekj/ontap-api-wrapper',
      download_url='https://github.com/machalekj/ontap-api-wrapper/archive/v0.5.3.tar.gz',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ]
     )

