import os
from setuptools import setup, find_packages

from onepanel.constants import *

install_requires=[
    'configparser',
    'PyYAML<=3.13,>=3.10',
    'prettytable',
    'requests<3.0.0dev,>=2.18.0',
    'click>=7',
    'PTable',
    'configobj',
    'websocket-client',
    'humanize',
    'botocore>=1.12.0,<1.13.0',
    'boto3>=1.9.0,<1.10.0',
    'watchdog',
    'iso8601',
    'future',
    'google-cloud-storage>=1.15.0'
]

if 'CLOUD_PROVIDER' in os.environ:
    install_requires.extend(['psutil', 'nvidia-ml-py3'])

setup(
    name=CLI_PACKAGE_NAME,
    version=CLI_VERSION,
    description='Onepanel CLI',
    author='Onepanel, Inc.',
    author_email='support@onepanel.io',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=install_requires,
    setup_requires=[
        # Need this here to ensure the right version of click is installed on the users machine.
        # Otherwise, they might get the 'hidden' error.
        'click>=7'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
