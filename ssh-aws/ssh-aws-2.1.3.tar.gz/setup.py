import setuptools
import awssh

VERSION = awssh.VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ssh-aws',
    version=VERSION,
    description='SSH into your EC2 instances.',
    author='Francisco Duran',
    author_email='franciscogd@gatech.edu',
    url='https://gitlab.com/franciscogd/awssh',
    download_url='https://gitlab.com/franciscogd/awssh/archive/{}.tar.gz'.format(VERSION),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'awscli>=1.10.14',
        'boto3>=1.3.1'
    ],
    classifiers=[
            "Programming Language :: Python :: 2.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    entry_points={
        'console_scripts': ['awssh = awssh:main'],
    }
)
