# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='aiobitcoin',
    version='0.72.2',
    description='Bitcoin lib for working with Bitcoin RPC.',
    author='mkbeh',
    author_email='mkbehforever@gmail.com',
    url='https://github.com/mkbeh/aiobitcoin',
    license='MIT',
    install_requires=[
        'aiohttp==3.5.4',
        'async-timeout==3.0.1',
        'attrs==19.1.0',
        'chardet==3.0.4',
        'idna==2.8',
        'idna-ssl==1.1.0',
        'multidict==4.5.2',
        'typing-extensions==3.7.2',
        'ujson==1.35',
        'yarl==1.3.0',
    ],
    packages=find_packages()
)
