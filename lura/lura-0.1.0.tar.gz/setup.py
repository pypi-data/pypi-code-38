from setuptools import setup, find_packages

install_requires = [
  'cryptography >= 2.7',
  'Jinja2 >= 2.10',
  'PyYAML >= 3.13',
  #'msgpack >= 0.6.1',
]

setup(
  name = 'lura',
  version = "0.1.0",
  author = 'eckso',
  author_email = 'eckso@eckso.io',
  description = 'syntactic sugar',
  packages = find_packages(),
  python_requires = ">= 3.6",
  install_requires = install_requires,
  include_package_data = True,
)
