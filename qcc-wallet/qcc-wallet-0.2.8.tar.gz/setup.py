#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

ver = '0.2.8'

setup(
    name='qcc-wallet',
    version=ver,
    description=(
        'All like QCC wallet manage business can from qcc-wallet. Web-mother include member manage, '
        'organization manage, and catalog manage. Especially qcc-wallet support authorization management.'
    ),
    long_description='Docs for this project are maintained at https://gitee.com/qcc100/qcc-wallet.git.',
    author='Yang Chunbo',
    author_email='ycb@microto.com',
    maintainer='Yang Chunbo',
    maintainer_email='ycb@microto.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/qcc100/qcc-wallet.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'rsa==4.0',
        'web3==4.9.1'
    ]
)
