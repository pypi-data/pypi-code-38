import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='alisson_cli',  
     version='0.1',
     scripts=['automation.py'] ,
     author="Alisson Machado",
     author_email="alisson.machado@gmail.com",
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
