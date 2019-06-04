from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pyraftlog',
      version='2.0.2',
      description='Pure Python implementation of the RAFT concencous algorithm',
      long_description=readme(),
      long_description_content_type='text/x-rst',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
      ],
      url='https://pypi.org/project/pyraftlog/',
      author='Peter Scopes',
      author_email='peter.scopes@nccgroup.trust',
      license='Copyright 2018 NCC',
      packages=['pyraftlog'],
      install_requires=[
          'msgpack>=0.6.1',
          'redis>=3.0.0',
      ],
      entry_points={
          'console_scripts': ['pyraftlog-mock=pyraftlog.mock:main',
                              'pyraftlog-migrate=pyraftlog.migrate:main']
      },
      include_package_data=True,
      zip_safe=False)
