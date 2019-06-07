import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='int_py',  
     version='0.0.13',
     scripts=['intpy/intpy.py'] ,
     author="UFF",
     author_email="alyssongomes@id.uff.br",
     description="",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/dew-uff/intPy-eScience",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
     ]
 )
