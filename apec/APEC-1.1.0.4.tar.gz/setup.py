#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='APEC',
    version='1.1.0.4',
    description='Single cell epigenomic clustering based on accessibility pattern',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Bin Li',
    author_email='libinsnet@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/QuKunLab/APEC',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    install_requires=[
        'numpy',
        'scipy==1.0.0',
        'pandas',
        'matplotlib',
        'seaborn',
        'numba',
        'networkx',
        'python-louvain==0.11',
        'scikit-learn==0.20.0',
        'MulticoreTsne',
        'umap-learn',
        'rpy2==2.8.5',
        'setuptools'
    ]
)
