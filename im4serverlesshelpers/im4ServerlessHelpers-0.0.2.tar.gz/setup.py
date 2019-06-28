# https://python-packaging.readthedocs.io/en/latest/minimal.html
# python3 setup.py register sdist upload

from setuptools import setup, find_packages

setup(name='im4ServerlessHelpers',
      version='0.0.2',
      author='Agroneural',
      author_email='admin@agroneural.com',
      packages=find_packages(),
      zip_safe=False)
