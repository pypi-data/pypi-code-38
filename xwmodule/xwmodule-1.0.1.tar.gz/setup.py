from distutils.core import setup
from setuptools import find_packages
 
setup(name = 'xwmodule',
      version = '1.0.1',
      description = 'python module demo',
      long_description = '',
      author = 'xwann',
      author_email = '1220936030@qq.com',
      url = '',
      license = '',
      install_requires = [],
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
      ],
      keywords = 'demo',
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data = True,
)