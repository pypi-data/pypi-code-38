#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='py_nsbcli',
    version='0.5.19',
    description=(
        'interacting with Tendermint-NSB from python'
    ),
    long_description=open('README.md').read(),
    author='Myriad Dreamin',
    author_email='xyangxi5@gmail.com',
    maintainer='Myriad-Dreamin',
    maintainer_email='xyangxi5@gmail.com',
    license='BSD 3-Clause "New" or "Revised" License',
    packages=find_packages(),
    platforms=["MacOS", "Windows"],
    install_requires=['hexbytes', 'requests', ],
    url='https://github.com/Myriad-Dreamin/py-nsbcli',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        # planing 'Operating System :: OS Independent',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7'
    ]
)