# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='cdstarcat',
    version="1.0.0",
    description='Manage objects in a CDSTAR instance through a catalog',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://github.com/clld/cdstarcat',
    license="Apache 2",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'clldutils>=2.0',
        'pycdstar>=1.0.0',
        'attrs>=18.1',
    ],
    extras_require={
        'dev': [
            'tox',
            'flake8',
            'wheel',
            'twine',
        ],
        'test': [
            'mock',
            'pytest>=3.6',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    entry_points={
        'console_scripts': [
            'cdstarcat=cdstarcat.__main__:main',
        ]
    },
)
