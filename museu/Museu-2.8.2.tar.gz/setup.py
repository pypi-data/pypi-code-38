from distutils.core import setup
from setuptools import find_packages
#导入setup函数
 
setup(
	  name="Museu", 
	  version="2.8.2",
	  description="常用工具包",
	  author="blackstone",
	  author_email="971406187@qq.com",
	  url="https://github.com/Blackstone1204",
	  #py_modules=['morm']
	  packages=find_packages(),
	  package_data = {
	  # If any package contains *.txt or *.rst files, include them:
	  '': ['*.yaml']
	  # include any *.msg files found in the 'hello' package, too:
	  # 'config': ['*.yaml']
		}

	  )