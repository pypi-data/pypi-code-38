import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = '0.0.3'


class VerifyVersionCommand(install):
    description = 'verify that git tag matches VERSION prior to publishing to pypi'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = 'Git tag: {0} does not match the version of this app: {1}'.format(
                tag, VERSION
            )
            sys.exit(info)


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


install_requires = [
    'boto3==1.9.169'
]

setup(
    name='cheapodb',
    version=VERSION,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    url='https://github.com/mineralzen/cheapodb',
    keywords=['data', 'aws'],
    packages=find_packages(exclude=('test*',)),
    package_dir={'directaccess': 'directaccess'},
    license='MIT',
    author='Cole Howard',
    author_email='cole@mineralzen.com',
    description='Opinionated implementation of AWS Glue',
    cmdclass={
        'verify': VerifyVersionCommand,
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
