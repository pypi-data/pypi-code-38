import os
from setuptools import setup

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'ems_client/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='UW-EMS-Client',
    version=VERSION,
    packages=['ems_client'],
    include_package_data=True,
    install_requires=[
        'CommonConf>=0.6,<1.0 ; python_version<"3"',
        'CommonConf>=0.6 ; python_version>="3"',
        'lxml',
        'python-dateutil',
        'suds-community',
        'UW-RestClients-Core<1.0 ; python_version<"3"',
        'UW-RestClients-Core ; python_version>="3"',
    ],
    tests_require=[
        'nose2',
        'pycodestyle',
    ],
    license='Apache License, Version 2.0',
    description='A client for the EMS SOAP API',
    long_description='README.md',
    url='https://github.com/uw-it-cte/uw-ems-client',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Scheduling',
    ],
)
