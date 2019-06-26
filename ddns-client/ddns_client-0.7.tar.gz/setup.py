# -*- coding: utf-8 -*-
import ddns_client
import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements/install.txt', 'r', encoding='utf-8') as f:
    install_requires = f.readlines()


setuptools.setup(
    name='ddns_client',
    version=ddns_client.__version__,
    author='fun04wr0ng',
    author_email='fun04wr0ng@gmail.com',
    description='ddns_client, used with coredns/etcd',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fun04wr0ng/ddns',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux'
    ],
    license='GPL v3',

    python_requires='>=3.6',
    install_requires=install_requires,
    extras_require={
        'color': [
            'coloredlogs',
        ],
        'fluentd': [
            'fluent-logger'
        ],
        'statsd': [
            'statsd'
        ],
        'prometheus': [
            'prometheus_client'
        ],
        'etcd': [
            'etcd3'
        ]
    },
    entry_points={
        'console_scripts': [
            'ddns_client = ddns_client.ddns_client:main',
        ],
    },
    package_data={
        '': ['*.yml', ]
    }
)
