
import os
import re

from setuptools import setup


def package_data_rec(package, directory):
    paths = []
    for path, directories, filenames in os.walk(os.path.join(package, directory)):
        for filename in filenames:
            paths.append(os.path.join(path, filename)[len(package) + 1:])

    return paths


def find_version():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colibrissendgrid', '__init__.py')) as f:
        m = re.search(r"VERSION\s*=\s*'(.*?)'", f.read())
        if m:
            return m.group(1)

    return 'unknown'


setup(
    name='colibris-sendgrid',
    version=find_version(),
    install_requires=[
        'aiohttp',
        'colibris'
    ],
    url='http://gitlab.com/safefleet/colibris-sendgrid',
    license='BSD',
    description='SendGrid email backend for Colibris',
    packages=['colibrissendgrid']
)
