from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='dacq2py',
	  version='0.1.7',
	  description='Analysis of electrophysiological data recorded with the Axona recording system',
	  long_description=long_description,
	  long_description_content_type='text/markdown',
	  url='https://github.com/rhayman/dacq2py',
	  author='Robin Hayman',
	  author_email='r.hayman@ucl.ac.uk',
	  license='MIT',
	  packages=['dacq2py'],
	  python_requires='>=3',
	  install_requires=[
	  	'numpy',
	  	'scipy',
	  	'matplotlib',
	  	'astropy',
	  	'scikit-image',
	  	'mahotas',
	  	'scikits.bootstrap'
	  ],
	  zip_safe=False)
