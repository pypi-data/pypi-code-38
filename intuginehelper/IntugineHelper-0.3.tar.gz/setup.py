
from setuptools import setup, find_packages


setup(
     name='IntugineHelper',  
     version='0.3',
     author="Rishabhdeep Singh",
     author_email="rishabhdeepsingh98@gmail.com",
     description="A Helper for Intugine",
     long_description=open('README.md','r').read(),
     long_description_content_type="text/markdown",
     url="https://github.com/rishabhdeepsingh/IntugineHelper",
     packages=find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
