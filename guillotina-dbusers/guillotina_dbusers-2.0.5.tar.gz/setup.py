# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name='guillotina_dbusers',
    version=open('VERSION').read().strip(),
    description='guillotina addon to provide users that are stored in the database',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGELOG.rst').read()),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['async', 'guillotina', 'users', 'auth'],
    author='Nathan Van Gheem',
    author_email='vangheem@gmail.com',
    url='https://pypi.python.org/pypi/guillotina_dbusers',
    license='GPL version 3',
    setup_requires=[
        'pytest-runner',
    ],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']),
    install_requires=[
        'setuptools',
        'guillotina>=4.2.1,<5.0.0',
    ],
    tests_require=[
        'pytest',
    ],
    extras_require={
        'test': [
            'pytest',
            'requests'
        ]
    }
)
