from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='critical_path',
      version='0.0.6',
      description='Tools for adapting universal language models to specifc tasks',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ltskinner/critical-path-nlp',
      author='ltskinner',
      keywords='BERT google transformer squad SQuAD nlp',
      license='Apache',
      install_requires=['tensorflow'],
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      zip_safe=False)
