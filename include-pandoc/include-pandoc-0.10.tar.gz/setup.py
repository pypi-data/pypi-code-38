from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='include-pandoc',
     version='0.10',
     scripts=['include_pandoc/include-pandoc'] ,
     author="Alberto Pianon",
     author_email="pianon@array.eu",
     description="A wrapper for pandoc to pre-process includes (even nested ones)",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/alpianon/include-pandoc",
     packages=['include_pandoc'],
     classifiers=[
         "Programming Language :: Python :: 2.7",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3) ",
         "Operating System :: OS Independent",
     ],
     install_requires=[
        'argparse',
     ],
 )
