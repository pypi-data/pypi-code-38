# Always prefer setuptools over distutils
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(name                  		=   'import_nbmodule',
      version               		=   '0.0.2',
      description           		=   'import jupyter notebook .ipynb module',
      long_description      		=   long_description,
      long_description_content_type	=	"text/markdown",
      author 						= 	"Lingling Yang",
      author_email 					= 	"yll0620@gmail.com",
      py_modules            		=   ['import_nbmodule'],
      packages 						= 	find_packages(),
      # the project's homepage
      url                   		=   'https://github.com/yangll0620/import_nbmodule',
      classifiers					= [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      ],
)