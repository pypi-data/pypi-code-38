#!/usr/bin/env python

from setuptools import setup

with open('README.md', 'r') as f:
    long_desc = f.read()

with open('requirements.txt', 'r') as f:
    install_reqs = f.read().splitlines()

setup(
    name='armmwave',
    version='0.0a2',
    author='Andrew Nadolski',
    author_email='andrew.nadolski@gmail.com',
    description='Calculate mm-wave transmittance and reflectance of materials',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    platforms=['Linux', 'MacOS X'],
    url='https://github.com/anadolski/armmwave',
    install_requires=install_reqs,
    python_requires='>=3.5',
    package_dir={'armmwave': 'armmwave'},
    packages=['armmwave'],
    tests_require=['pytest'],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 3 - Alpha',
        ],
    )
