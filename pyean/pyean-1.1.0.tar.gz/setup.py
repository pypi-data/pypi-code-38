# -*- coding: utf-8 -*-

from pathlib import Path
from setuptools import find_packages, setup


setup(
    name='pyean',
    packages=find_packages(),
    license='MIT',
    author='Mrsamkhar',
    author_email='mydevelopmentspace@gmail.com',
    description=(
        'Create standard barcodes with Python. Only EAN13. '
        '(optional Pillow support included).'
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'pyean = barcode.pybarcode:main',
        ],
    },
    use_scm_version={
        'version_scheme': 'post-release',
        'write_to': 'pyean/version.py',
    },
    setup_requires=['setuptools_scm'],
    extras_require={
        'images': ['pillow']
    },
    include_package_data=True,
)
