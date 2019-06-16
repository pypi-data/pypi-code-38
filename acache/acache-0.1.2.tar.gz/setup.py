#!/usr/bin/env python3


from setuptools import setup


VERSION = '0.1.2'
REQUIREMENTS = 'requirements.txt'


def parse_file(path):
    with open(path, 'r') as f:
        req = f.read().split('\n')
    return req


setup(
    name='acache',
    version=VERSION,
    description='An extremely versatile and lightweight cache library.',
    license='MIT',
    packages=['acache', 'acache.strategy', 'acache.strategy.hash'],
    zip_safe=True,
    include_package_data=True,
    install_requires=parse_file(REQUIREMENTS),
)
