from setuptools import setup,find_packages
import sys
import datetime

PROJECT_NAME = 'uforge_python_sdk'
PROJECT_VERSION = '3.8.13'

setup (

  # Declare your packages' dependencies here, for eg:
  install_requires=[
      'lxml==3.3.5',
      'pyxb==1.2.4',
      'requests==2.13.0'
  ],
  package_data={'uforge': ['config/*',]},

  name = PROJECT_NAME,
  version = PROJECT_VERSION,
  packages = find_packages(),

  description='UForge python SDK',
  long_description='',
  author = 'UShareSoft',
  author_email = 'contact@usharesoft.com',
  license="Apache License 2.0",
  url = '',
  classifiers=(
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
