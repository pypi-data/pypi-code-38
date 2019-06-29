#!/usr/bin/env python
from setuptools import find_packages, setup
packages = find_packages()

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "0.1.4"
setup(name='mgpro',
      version=VERSION,
      author='Mijian Xu',
      author_email='gomijianxu@gmail.com',
      url='https://github.com/xumi1993/MGPro',
      description='A Python Interactive command line toolbox for processing geomagnetic and gravity data',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='GPLv3',
      packages=find_packages(),
      package_dir={'MGPro': 'mgpro'},
      install_requires=['pyproj', 'numpy', 'scipy', 'matplotlib'],
      entry_points={'console_scripts': ['mgpro=mgpro.client:main',
                                        'proj_convert=mgpro.proj:exec']},
      include_package_data=True,
      zip_safe=False
      )
