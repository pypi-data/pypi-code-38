 #!/usr/bin/env python
 
from setuptools import setup, find_packages
setup(
name='pyscratch',
version='0.2.6',
description='Education tool, provide scratch enviroment and API in python, help children learn python easily',
keywords='pyscratch scratch children education learn python game easy',
author='shaolizhi',
author_email='53733522@qq.com',
license='MIT',
url='http://www.openscratch.com/',
include_package_data=True,
packages=find_packages(),
install_requires=[
        'pygame'
    ]
)
