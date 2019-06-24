from setuptools import setup

setup(name='satellitetle',
      version='0.7.0',
      description='Fetch satellite TLEs from various online sources',
      url='https://gitlab.com/librespacefoundation/python-satellitetle',
      author='Fabian P. Schmidt',
      author_email='kerel-fs@gmx.de',
      license='MIT',
      long_description=open('README.rst').read(),
      packages=['satellite_tle'],
      install_requires=[
          'lxml',
          'requests',
          'sgp4',
      ],
      package_data={'satellite_tle': ['sources.csv']},
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
      ],
      )
