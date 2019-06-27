# -*- coding: utf-8 -*-
#
# This file is part of ProjectBubble.
#
# (c) Giant - MouGuangyi <mouguangyi@ztgame.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from setuptools import setup


def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


setup(
    name='GXBubble',
    version='0.1.27',
    packages=['gxbubble'],
    url='',
    license='MIT',
    author='mouguangyi',
    author_email='mouguangyi@ztgame.com',
    description='GameBox Bubble Python Package',
    long_description=readme(),
    install_requires=[
    ],
    include_package_data=True,
    dependency_links=[
    ],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose']
)

