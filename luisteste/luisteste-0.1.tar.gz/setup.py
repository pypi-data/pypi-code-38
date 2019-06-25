import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='luisteste',  
     version='0.1',
     scripts=['stone_cli.py'] ,
     author="Luis C",
     author_email="luis.cipparrone@stone.com.br",
     description="pacote criado na aula1",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/AlissonMMenezes/teste",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
