from setuptools import setup, find_packages

setup(
  name = 'hktools',
  version = '0.1.0',
  keywords='toolbox',
  description = 'a toolbox for Deep Learning Developer',
  license = 'MIT License',
  url = 'https://github.com/iamhankai/hktools',
  author = 'Kai Han',
  author_email = 'kaihana@163.com',
  packages = find_packages(),
  include_package_data = True,
  platforms = 'any',
  classifiers=[
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence'
  ],
  install_requires = [],
)
