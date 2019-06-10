import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='ansible-ssh',  
     version='0.1',
     scripts=['ansible-ssh'] ,
     author="Dimos Alevizos",
     author_email="dimos.alevizos@pan-net.eu",
     description="Interactive SSH for Ansible",
     long_description=long_description,
   long_description_content_type="text/markdown",
     #url="https://github.com/javatechy/dokr",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 2",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
