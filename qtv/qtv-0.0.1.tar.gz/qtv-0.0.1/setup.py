#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='qtv',
    version='0.0.1',
    author='Fangzhou Wang',
    author_email='fwangusc@gmail.com',
    license='Apache Software License',
    keywords='RSFQ STA DTV ATPG',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6, !=3.5.*, <4',
    packages=find_packages(exclude=['outputs', 'rsfq_lib', 'unit_tests']),
    install_requires=[
        'arklibpy>=0.1.5',
        'tqdm',
        'numpy',
        'matplotlib',
    ],
    test_suite='unit_tests',
)
