#!/user/bin/env python
#!-*- coding:utf-8 -*-
'''
Created on 20190506
@auther: dq
'''
from setuptools import setup,find_packages
setup(name = 'kdbase',
      version= '1.10',
      keywords = ('pip', 'kdbase', 'featureextraction'),
      description = 'Custom script',
      license = 'MIT Licence',
      url = 'http://songyanjing@git.kuandeng.com/scm/tin/bigdata_support.git',
      author = 'dq',
      author_email = 'duquan@kuandeng.com',
      packages = find_packages(),
      include_package_data = True,
      platforms = "any"
      #packages = ['kd_infra'],
     )
