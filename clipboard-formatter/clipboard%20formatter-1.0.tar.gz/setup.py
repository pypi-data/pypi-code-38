#!/usr/bin/env python
from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
	reqs = f.read().splitlines()

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
   name='clipboard formatter',
   version='1.0',
   description='Takes copied text and formats to be used in SQL list',
   long_description=readme(),
   url='https://github.com/usolek/simple-utils',
   author='Ulysses Olek',
   author_email='uskovolek@gmail.com',
   license='MIT',
   packages=find_packages(),  #same as name
   install_requires=reqs, #external packages as dependencies
   entry_points = {
        'console_scripts': ['clipform=clipform.command_line:main']
        }
)
