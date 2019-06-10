from setuptools import find_packages, setup

full_description = '''\
This is a simple dependencies manager for Python 3 that creates an isolated virtual environment for your project.
Just add your dependencies into the caos.json config file and use some console commands to run your projects.

Please take a look at our full documentation for how to install and use caos:    
* GitHub page: <https://github.com/ospinakamilo/caos/>

caos.json
```json
{
    "require":{
        "flask": "latest"
    },

    "tests" : "./tests",
    "main": "./src/main.py" 
}
```
Caos console commands:
```console
username@host:~$ caos init     #Create the caos.json file in the current directory
```  
```console
username@host:~$ caos prepare  #Set up a new virtual environment
```
```console
username@host:~$ caos update   #Download the project dependencies into the virtual environment
``` 
```console
username@host:~$ caos check    #Validate the dependencies have been downloaded
```
```console
username@host:~$ caos test     #Execute all the unit tests available using the unnittest framework
```
 ```console
username@host:~$ caos run      #Run the main script of the project
```
```console
username@host:~$ caos run arg1 #Run the main script of the project sending some argument 
```
```console
username@host:~$ caos --help     #Get a similar set of instructions to the ones shown here
```
```console
username@host:~$ caos --version  #Display the current installed version
```
'''


setup(
    name="caos",  
    version="1.2.0",
    author="Team Camilo",
    author_email="camilo.ospinaa@gmail.com",
    description="Simple Dependency Management for Python 3 Projects using pip and virtualenv",
    long_description=full_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ospinakamilo/caos/",
    keywords='caos virtualenv dependencies manager ppm pipenv venv distutils easy_install egg setuptools wheel',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],

    package_dir={"": "src"},

    packages=find_packages(
        where="src",
        exclude=["docs", "tests"],
    ),    

    entry_points={
        "console_scripts": ["caos=caos:console"],
    },

    install_requires=[
        'pip>=8.0.0',
        'virtualenv>=14.0.0',
    ],

    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*,  <4",
    
 )
