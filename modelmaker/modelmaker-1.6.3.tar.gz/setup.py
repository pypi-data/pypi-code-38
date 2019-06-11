#conding:utf-8
#https://setuptools.readthedocs.io/en/latest/setuptools.html
#import os
from setuptools import setup, find_packages

setup(name='modelmaker',
      version='1.6.3',
      description='Wangsu ai sdk',
      author='wangjm',
      author_email='wangjm2@wangsu.com',
	  long_description=open('README.rst').read(),
	  url='https://github.com/AiModelMaker/ModelMaker',
      packages=find_packages(),
	  include_package_data=True,
	  license='MIT',
      install_requires=['requests>=2.14.2', 'urllib3<1.25,>=1.21.1', 'boto3>=1.4.5','botocore>=1.5.92'],
      python_requires='>=3',
	  classifiers=[
		#   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
	  'Development Status :: 4 - Beta',
	  'Operating System :: OS Independent',
	  'Intended Audience :: Developers',
	  'License :: OSI Approved :: MIT License',
	  'Programming Language :: Python :: Implementation',
	  'Programming Language :: Python :: 3.6',
	  'Topic :: Software Development :: Libraries'
	  ],
)
