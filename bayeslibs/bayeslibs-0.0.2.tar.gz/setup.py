# conding=utf-8
"""
@project:bayeslibs
@language:Python3
@create:2019/6/27
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# 导入静态文件
file_data = [
    ("bayeslibs/config", ["bayeslibs/config/apollo.ini"]),
]

setup(name='bayeslibs',
      version='0.0.2',
      description='The bayeslibs is the best ai education libs in the world',
      author='bayes',
      long_description=long_description,
      long_description_content_type="text/markdown",
      data_files=file_data,
      include_package_data=True,  # 是否需要导入静态数据文件
      author_email='qianyang@aibayes.com',
      install_requires=['baidu-aip', 'numpy', 'opencv-python'],
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
