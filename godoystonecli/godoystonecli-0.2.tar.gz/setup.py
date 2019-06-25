import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='godoystonecli',  
     version='0.2',
     scripts=['stone_cli'] ,
     author="Fernando Godoy",
     author_email="fgodoy@stone.com.br",
     description="Cria tudo automático",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/blabla",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )

 #python setup.py sdist bdist_wheel
 #python -m twine upload dist/*