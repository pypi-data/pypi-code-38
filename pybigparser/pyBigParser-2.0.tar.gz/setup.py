# setup.py

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
	
setuptools.setup(
    name='pyBigParser',
    version='2.0',
    author='Nelson Carrasquel',
    author_email='carrasquel@outlook.com',
	description="Math parser for simple and compound strings math expressions evaluations",
	long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    packages=['pybigparser',],
    license='BSD License',
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
