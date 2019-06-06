#!/usr/bin/env python

import setuptools

with open('README.md', 'r') as fh:

    long_description = fh.read()

setuptools.setup(
    name='smsframework-africastalking',
    version='1.0.2',
    author='BBOXX',
    author_email='j.lynch@bboxx.co.uk',
    description='SMS framework: Africa\'s Talking provider',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BBOXX/py-smsframework-africastalking',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    keywords='sms message send africa africastalking smsframework provider'
)
