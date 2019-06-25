import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='stoneclivmcreator',  
     version='0.1',
     scripts=['stone_cli.py'] ,
     author="Elnatan Torres",
     author_email="elnatannovaes@hotmail.com",
     description="Script that creates virtual machines at GCP or Azure",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/elnatantorres/virtual-machine-creator.git",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )