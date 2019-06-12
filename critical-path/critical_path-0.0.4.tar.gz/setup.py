from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='critical_path',
      version='0.0.4',
      description='Tools for adapting universal language models to specifc tasks',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ltskinner/critical-path-nlp',
      author='ltskinner',
      license='MIT',
      install_requires=['tensorflow'],
      packages=['critical_path'],
      zip_safe=False)
