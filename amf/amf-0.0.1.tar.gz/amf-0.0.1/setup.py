import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='amf',  
     version='0.0.1',
     scripts=['amf'] ,
     author="Vinita Phadke",
     author_email="vini.phadke12@gmail.com",
     description="Automated Modelling Framework Package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/vini-1208/amf.git",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )