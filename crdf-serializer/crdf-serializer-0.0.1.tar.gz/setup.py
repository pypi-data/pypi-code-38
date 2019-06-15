import setuptools

with open ( "README.md" , "r" ) as fh :
    long_description = fh . read ()

setuptools . setup (
    name = "crdf-serializer" ,
    version = "0.0.1" ,
    author = "Prof. Sergio Costa" ,
    author_email = "prof.sergio.costa@gmail.com" ,
    description = "Some decorators responsible for preparing and serializing RDF files." ,
    long_description = long_description ,
    long_description_content_type = "text/markdown" ,
    url = "https://github.com/vittorduartte/crdf_serializer" ,
    packages = setuptools . find_packages (),
    classifiers = [
        "Programming Language :: Python :: 3" ,
        "License :: OSI Approved :: MIT License" ,
        "Operating System :: OS Independent" ,
    ],
)