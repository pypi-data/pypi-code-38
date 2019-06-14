from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='lepmlutils',  
     version='2.0.10',
     scripts=['mlutils'] ,
     author="Louka Ewington-Pitsos",
     author_email="lewington@student.unimelb.edu.au",
     description="A machine learning utility package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/Lewington-pitsos/mlutils",
     packages=['lepmlutils', 'lepmlutils.xgbutils', 'lepmlutils.pdutils'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[
        'sklearn',
        'xgboost',
    ],
 )