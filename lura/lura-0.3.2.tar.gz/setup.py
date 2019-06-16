from setuptools import setup, find_packages

name             = 'lura'
version          = '0.3.2'
author           = 'eckso'
author_email     = 'eckso@eckso.io'
url              = 'https://github.com/ecks0/lura'
description      = 'syntactic sugar'
long_description = open('README.md').read()
long_description_content_type = 'text/markdown'
python_requires  = ">= 3.6"
install_requires = [
  'Jinja2 >= 2.10',
  'PyYAML >= 3.13',
  'cryptography >= 2.7',
  'ptyprocess >= 0.6.0',
]

setup(
  name = name,
  version = version,
  author = author,
  author_email = author_email,
  description = description,
  long_description = long_description,
  long_description_content_type = long_description_content_type,
  python_requires = python_requires,
  install_requires = install_requires,
  packages = find_packages(),
  include_package_data = True,
)
