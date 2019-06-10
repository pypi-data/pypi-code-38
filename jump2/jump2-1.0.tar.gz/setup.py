# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

import shutil
from setuptools import find_packages, setup
import os, sys

# package name % 
name='jump2'

# version % 
version = '1.0'

# authors %
authors='jump2 team'
authors_email='lijun_zhang@jlu.edu.cn'

# maintainer % 
maintainers='Xin-Gang Zhao, Yuhao Fu, Guangren Na, Shulin Luo'

# maintainer emails %
maintainer_email='xgzhao0201@gmail.com,\
                  fuyuhaoy@gmail.com,\
                  guangrenna@gmail.com,\
                  shulinluo999@gmail.com'
# license % 
license='Jilin University, Version 1.0'

# description % 
description = 'Python Package for High Throughput \
               Materials-design calculation.'

# required packages %
requires=[]
#requires=['ipython >= 2.0','django  >= 1.7',\
#          'numpy   >= 1.6.0', 'ase >= 2.0',\
#	  'spglib  >= 1.0']

# jump2 packages.
package= [name] + ['%s.%s' % (name, i) \
          for i in find_packages(name)]

# optional required packages.
#setup (install_requires=['numpy >= 1.6.0'])

setup(
      name=name,
      version=version,
      author=authors,
      author_email=authors_email,
      maintainer=maintainers,
      maintainer_email=maintainer_email,
      license = license,
      description = description,
      platforms= 'Linux',
      install_requires= requires,
      packages = package)


# option setting if possible % 
#if not os.path.exists('/home/gordon/.local/jump2/bin/jump2'):

#    os.makedirs('/home/gordon/.local/jump2/bin')
#    shutil.copy('jump2.x', '/home/gordon/.local/jump2/bin/jump2')
#    os.system('export PATH=/home/gordon/.local/jump2/bin:$PATH')


