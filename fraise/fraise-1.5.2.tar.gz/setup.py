import os

from setuptools import setup, find_packages

setup(name='fraise',
      version='1.5.2',
      description='Generate memorable pass phrases',
      long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      long_description_content_type="text/markdown",
      url='http://github.com/daveygit2050/fraise',
      author='Dave Randall',
      author_email='dave@goldsquare.co.uk',
      license='Apache v2',
      packages=find_packages(exclude=('tests', 'docs', 'target')),
      zip_safe=False,
      entry_points={'console_scripts': ['fraise=fraise.application:run']})
