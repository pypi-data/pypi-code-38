# -*- coding: utf-8 -*-
"""
Created on Tue May 21 18:07:20 2019

@author: steph
"""

from setuptools import setup, find_packages

setup(

    name='wordvecpy',
    url='https://github.com/metriczulu/wordvecpy',
    author='Shane Stephenson',
    author_email='stephenson.shane.a@gmail.com', 
    packages=find_packages(),
    install_requires = ['numpy', 'tqdm'],
    version='v0.71',
    license="All yours bro",
    description='Package for working with word vector embeddings',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r').read(),
    download_url = 'https://github.com/metriczulu/wordvecpy/archive/v0.71.tar.gz'
)
