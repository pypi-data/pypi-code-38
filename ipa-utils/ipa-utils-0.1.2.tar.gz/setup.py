# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "click",
    "ldap3",
]

setup(
    name="ipa-utils",
    version="0.1.2",
    description="Freeipa辅助工具。",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/appstore-zencore/ipa-utils",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['ipa-utils', 'ipa-utilsf'],
    install_requires=requires,
    packages=find_packages("."),
    py_modules=["ipa_utils"],
    entry_points={
        'console_scripts': [
            "ipa-utils = ipa_utils:ipa",
        ]
    },
)