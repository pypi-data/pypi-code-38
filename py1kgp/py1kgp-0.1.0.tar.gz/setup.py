import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='py1kgp',
    version='0.1.0',
    author='Anthony Aylward',
    author_email='aaylward@eng.ucsd.edu',
    description='Utilities for working with 1000 Genomes data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/py1kgp.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['pyhg19']
)
