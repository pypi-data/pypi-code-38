#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

from mailtrigger.version import VERSION


with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

setuptools.setup(
    author='Jia Jia',
    author_email='angersax@sina.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    description='Remote service trigger with mail',
    download_url='https://github.com/craftslab/mailtrigger/archive/v%s.tar.gz' % VERSION,
    entry_points={'console_scripts': ['mailtrigger=main:main']},
    include_package_data=True,
    install_requires=requirements,
    keywords=['gerrit', 'jenkins', 'jira', 'mail', 'mailtrigger', 'trigger'],
    license='Apache-2.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='mailtrigger',
    packages=setuptools.find_packages(),
    url='https://github.com/craftslab/mailtrigger',
    version=VERSION,
    zip_safe=False)
