import sys
from setuptools import setup, find_packages
from distutils.version import LooseVersion

if sys.hexversion < 0x30500f0:
    print('Stex API client requires at least Python 3.5')
    sys.exit(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='stex-client',
    description='Stex API V3 client for python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/StocksExchange/python_client',
    version=str(LooseVersion('1.0.3')),
    packages=find_packages(),
    python_requires='>=3.5',
    author='STEX (Stocks.Exchange)',
    license='MIT',
    copyright='Copyright (C) 2019 Stex.com',
    author_email='analytics@stex.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='api client request stocks.exchange stex library websocket-client stex.com',
    install_requires=[
        'requests',
        'furl',
        'pendulum',
        'python-socketio'
    ],
)
