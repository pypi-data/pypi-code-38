#!/usr/bin/python

""""""

from setuptools import setup


setup(
    name='server-dev',

    version='1.0.4',

    description='Server administration tools',

    url='',
    project_urls={
        'Documentation': 'https://caidenpyle.com/api_docs'
    },

    author='Caiden Pyle',
    author_email='caiden.pyle@netapp.com',

    license='MIT',

    classifiers=[
        'Development Status :: 1 - Planning',

        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',

        'Topic :: Utilities',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        'License :: Freeware',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='api esx esxi vmware',
    required_packages=[],

    packages=['serverdev'],
)
