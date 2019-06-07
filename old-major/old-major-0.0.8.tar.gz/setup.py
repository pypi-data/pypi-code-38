from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='old-major',

    version='0.0.8',

    description='RICC project central system',

    url='https://github.com/ricc-project/old-major',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['websocket_client', 'getmac', 'requests', 'inotify'],

    entry_points={
        'console_scripts': [
            'old-major = src.old_major:main',
        ],
    },
)
