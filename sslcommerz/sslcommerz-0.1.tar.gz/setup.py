import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='sslcommerz',  
     version='0.1',
     scripts=['sslc'] ,
     author="Rabiul Islam",
     author_email="rabiulislam993@live.com",
     description="Payment integretion for SSLCOMMERZ",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/rabiulislam993/sslcommerz",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
