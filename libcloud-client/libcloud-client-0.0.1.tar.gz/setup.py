#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':

    setup(
        name='libcloud-client',
        version='0.0.1',
        description='A lightweight Python client for LibCloud.',
        author='Yoginth',
        author_email='me@yoginth.com',
        url='https://gitlab.com/libcloud/libcloud-client',
        packages=['libcloud_client'],
        package_data={},
        data_files={},
        install_requires=["boto3"],
        license="Apache License 2.0",
        classifiers=[
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "License :: OSI Approved :: Apache Software License",
            "Topic :: Software Development :: Testing",
        ]
    )
