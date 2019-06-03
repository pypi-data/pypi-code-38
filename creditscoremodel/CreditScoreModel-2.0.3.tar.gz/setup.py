#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='CreditScoreModel',
    version='2.0.3',
    description=('CreditScoreModel'),
    long_description=open('README.rst',encoding='utf-8').read(),
    author='chengsong',
    author_email='990020186@qq.com',
    maintainer='chengsong',
    maintainer_email='990020186@qq.com',
    license='BSD License',
    # packages=find_packages(),
    packages=['CreditScoreModel'],
    platforms=["all"],
    url='https://github.com/chengsong990020186/CreditScoreModel',
    install_requires=['numpy','pandas','matplotlib','scikit-learn','tqdm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)