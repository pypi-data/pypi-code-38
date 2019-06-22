import sys
from setuptools import setup, find_packages
import setuptools
from os import path
from io import open

if sys.version_info < (3, 0):
    sys.stderr.write("Sorry, Python < 3.0 is not supported\n")
    sys.exit(1)


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='darksky_scraper',
      version='0.2.1',
      description="""A simple scraper for darksky.net.""",
      url='https://github.com/jimbob88/darksky_scraper',
      author='James Blackburn',
      author_email='blackburnfjames@gmail.com',
      packages=['darksky_scraper'],
      py_modules=['darksky_scraper/check_values'],
      python_requires='>=3.0.*, <4',
      install_requires=['beautifulsoup4'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License'
      ],
      long_description=long_description,
      project_urls={
          'Bug Reports': 'https://github.com/jimbob88/darksky_scraper/issues',
          'Source': 'https://github.com/jimbob88/darksky_scraper'
      },
      long_description_content_type='text/markdown')
