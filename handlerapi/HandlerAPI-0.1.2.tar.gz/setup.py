import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='HandlerAPI',  
     version='0.1.2',
     scripts=['HandlerAPI/HandlerAPI.py'] ,
     author="Susi Eva",
     author_email="susipurba2@gmail.com",
     description="Parsing PR, Issue, Commit, and LOC data from GitHub REST API",
     long_description=long_description,
     long_description_content_type= "text/markdown",
     url="https://github.com/Susi-Eva/Parser",
     packages=setuptools.find_packages(),
     include_package_data = True,
     install_requires = [
                        ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.6",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )