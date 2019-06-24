import setuptools
  
with open("README.md", "r") as fh:
	
	long_description = fh.read()
 
	setuptools.setup(

	  name="montytestpackage",
	  version="0.0.1",
	  author="Craig Sanders",
	  author_email="blah@hotmail.com",
	  description='My Python Test package',
	  long_description=long_description,
	  long_description_content_type="text/markdown",
	  url="https://github.com/c-sanders/testpackage",
	  packages=setuptools.find_packages(),
	  classifiers=[
	    "Programming Language :: Python :: 3",
	    "License :: OSI Approved :: MIT License",
	    "Operating System :: OS Independent",
	  ],
	)
