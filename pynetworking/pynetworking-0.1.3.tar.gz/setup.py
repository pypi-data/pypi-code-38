from setuptools import setup, find_packages
import unittest

with open("README.rst", "r") as fh:
    long_description = fh.read()


def my_test_suite():
    from pynetworking.Logging import logger
    logger.setLevel(0)
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('pynetworking.tests', pattern='test_*.py')
    return test_suite


if __name__ == '__main__':
    setup(name='pynetworking',
          version='0.1.3',
          description='High level network communication',
          long_description=long_description,
          url='https://github.com/JulianSobott/pynetworking',
          author='Julian Sobott',
          author_email='julian.sobott@gmx.de',
          license='Apache',
          packages=find_packages(),
          test_suite='setup.my_test_suite',
          include_package_data=True,
          keywords='network packet communication',
          project_urls={
            "Bug Tracker": "https://github.com/JulianSobott/pynetworking/issues",
            "Documentation": "http://pynetworking.readthedocs.io/",
            "Source Code": "https://github.com/JulianSobott/pynetworking",
          },
          classifiers=[
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries",
            ],
          zip_safe=False,
          install_requires=['cryptography', 'thread-testing', 'dill']
          )
