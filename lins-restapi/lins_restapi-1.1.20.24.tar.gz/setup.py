#!/usr/bin/env python

import os
import sys
from distutils.core import setup
from setuptools import find_packages


def get_version():
    return open('version.txt', 'r').read().strip()

setup(
    author='Lucas Lehnen',
    author_email='lucas@lojaspompeia.com.br',    
    description='Classes e utilitarios para uso em apis rest com django.',        
    license='MIT',    
    name='lins_restapi',
    packages=find_packages(),    
    url='https://bitbucket.org/grupolinsferrao/pypck-lins-restapi/',
    version=get_version(),
)