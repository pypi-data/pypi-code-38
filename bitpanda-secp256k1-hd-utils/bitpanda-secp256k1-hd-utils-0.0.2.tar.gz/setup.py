from distutils.core import setup
from setuptools import find_packages

setup(name='bitpanda-secp256k1-hd-utils',
      version='0.0.2',
      packages=find_packages(),
      install_requires=['chainside-btcpy-multi==0.2.77'],
      description='Python tool for for tezos hd generation',
      author='Oskar Hladky',
      author_email='oskyks1@gmail.com',
      url='https://github.com/bitpanda-labs/secp256k1-hd-utils',
      python_requires='>=3',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ],
)
