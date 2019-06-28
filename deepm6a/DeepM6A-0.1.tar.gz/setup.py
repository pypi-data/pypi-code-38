import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='DeepM6A',  
     version='0.1',
     scripts=['deepm6a.py'] ,
     author="Fei Tan",
     author_email="tanfei2007@gmail.com",
     description="A package for detection and eclucidation of Methylation on N6-Adenine",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/tanfei2007/DeepM6A",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
     ],
 )
