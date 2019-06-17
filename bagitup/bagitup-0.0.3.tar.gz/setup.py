from setuptools import setup
import setuptools 
with open("README.md", "r") as fh:
    long_description = fh.read()

 
setuptools.setup(
    #Here is the module name.
    name="bagitup",
 
    #version of the module
    version="0.0.3",
 
    #Name of Author
    author="Geetansh Jindal",
 
    #your Email address
    author_email="geetansh@hackreports.com",
 
    #Small Description about module
    description="bagitup is a Pythob based module that enables you to automatically backup your files and databases to Git",
 
    long_description=long_description,
 
    #Specifying that we are using markdown file for description
    long_description_content_type="text/markdown",
 
    #Any link to reach this module, if you have any webpage or github profile
    url="https://github.com/geetanshjindal/bagitup",
    packages=setuptools.find_packages(),

    install_requires=["environs"],

 
    #classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
