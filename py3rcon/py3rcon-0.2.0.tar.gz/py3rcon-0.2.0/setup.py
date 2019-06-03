import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='py3rcon',  

     version='0.2.0',

     scripts=['py3rcon.py'] ,

     author="Wiktor Metryka",

     author_email="jestemkiosk@gmail.com",

     description="Python3 wrapper for RCON communication.",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/Jestemkiosk/py3rcon",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: GNU General Public License (GPL)",

         "Operating System :: OS Independent",

     ],

 )