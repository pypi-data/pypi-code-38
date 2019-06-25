import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='arthurstonecli',  
     version='0.1',
     scripts=['stone_cli'] ,
     author="Arthur Machado",
     author_email="arthurmachado44@gmail.com",
     description="Cria a infraestrutura automatizada",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/Arthurmpc",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )


