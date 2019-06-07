from setuptools import setup
import setuptools

setup(name='mavnbclient',
      version='0.4',
      description='NB API wrapper for Bot development',
      url='https://github.com/Manoor00/MavNBClient',
      author='Sunil Manoor',
      author_email='sunil.manoor@mavenir.com',
      license='LGPL',
      packages=setuptools.find_packages(),
	   py_modules=["backports_abc", "singledispatch", "singledispatch_helpers"],
      zip_safe=True)
