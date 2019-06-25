import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='brunotanakastonecli',  
     version='0.2',
     scripts=['stone_cli'] ,
     author="Bruno Tanaka",
     author_email="bruno_tanaka100@ghotmail.com",
     description="Criar a infraestrutura automatizada de forma automatica",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/brunotanaka/stone_cli",
     packages=setuptools.find_packages(),
     classifiers=
     [
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )