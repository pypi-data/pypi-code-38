# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name='guillotina_mailer',
    version=open('VERSION').read().strip(),
    description='Mailer integration with guillotina',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGELOG.rst').read()),
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    keywords='async mail guillotina',
    license='BSD',
    zip_safe=True,
    author='Nathan Van Gheem',
    author_email='nathan.vangheem@wildcardcorp.com',
    url='https://github.com/pyrenees/guillotina_mailer',
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']),
    install_requires=[
        'setuptools',
        'guillotina>=4.0.0,<5.0.0',
        'html2text',
        'aiosmtplib'
    ],
    tests_require=[
        'pytest',
    ]
)
