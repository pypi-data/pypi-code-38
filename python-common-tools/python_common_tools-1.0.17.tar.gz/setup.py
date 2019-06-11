# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-05-06 17:46'

from setuptools import setup
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

if os.path.exists("README.md"):
    long_description = open("README.md", "r", encoding='utf-8').read()
else:
    long_description = "python common tools"

requirements = """
asn1crypto==0.24.0
autopep8==1.4.4
bcrypt==3.1.6
bleach==3.1.0
certifi==2019.3.9
cffi==1.12.3
chardet==3.0.4
cryptography==2.6.1
docutils==0.14
entrypoints==0.3
flake8==3.7.7
idna==2.8
logzero==1.5.0
mccabe==0.6.1
paramiko==2.5.0
pkginfo==1.5.0.1
pyasn1==0.4.5
pycodestyle==2.5.0
pycparser==2.19
pyflakes==2.1.1
Pygments==2.4.0
PyNaCl==1.3.0
readme-renderer==24.0
requests==2.22.0
requests-toolbelt==0.9.1
six==1.12.0
stackprinter==0.2.3
tqdm==4.32.1
twine==1.13.0
urllib3==1.24.2
webencodings==0.5.1
"""
install_requires = [i for i in requirements.split() if i]
setup(
    name='python_common_tools',
    version='1.0.17',
    python_requires='>3.6.0',
    author='chenzhang',
    author_email='1377699408@qq.com',
    url='https://github.com/CheungChan/python_common_tools',
    description='python common tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['python_common_tools'],
    install_requires=requirements,
    entry_points={
        "console_scripts": "test_pct=python_common_tools.test:main"
    }
)
