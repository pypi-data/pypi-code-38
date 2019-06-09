#!/usr/bin/env python
from setuptools import find_packages, setup

import versioneer


setup(
    name='dsdev-utils',
    version=versioneer.get_version(),
    description='Various utility functions',
    author='Digital Sapphire',
    author_email='digitalsapphire@gmail.com',
    url='https://github.com/JMSwag/dsdev-utils',
    download_url=('https://github.com/JMSwag/dsdev'
                  '-utils/archive/master.zip'),
    license='MIT',
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'chardet',
        'six',
        ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'],
    )
