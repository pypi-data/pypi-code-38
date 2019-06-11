# -*- coding: utf-8 -*
import os
from distutils.core import setup

NAME = 'zhangxulong'
_MAJOR = 0
_MINOR = 0
_MICRO = 8
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "utils @ZHANG Xu-long"

SEP = os.sep


def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['zhangxulong'],
    data_files=[('.' + SEP, ['CHANGELOG.md', 'README.md']),

                ]
    ,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    url='https://gitlab.com/zhangxulong',
    author_email="zhangxulong1009@gmail.com",
    license="BSD",
    keywords='audio music sound',
    classifiers=[
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",

    ]
)
