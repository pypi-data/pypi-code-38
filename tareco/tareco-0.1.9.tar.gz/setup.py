# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='tareco',
    version='0.1.9',
    url='https://github.com/naruminho/tareco',
    license='MIT License',
    author='Narumi Abe and Melissa Forti',
    author_email='mail.narumi@gmail.com',
    keywords='graph networks, plotly, networkx',
    description='A tool for plotting graph networks',
    packages=['tareco'],
    install_requires=['pandas', 'plotly', 'networkx','matplotlib'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Visualization'
    ]
)
